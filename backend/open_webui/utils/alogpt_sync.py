import asyncio
import hashlib
import hmac
import logging
import os
import re

import aiohttp
from fastapi import Header, HTTPException, status
from open_webui.env import AIOHTTP_CLIENT_SESSION_SSL
from open_webui.models.groups import GroupForm, Groups
from open_webui.models.users import Users
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)

SYNC_HEADER = 'X-Alogpt-Sync-Secret'
SOURCE_HEADER = 'X-Alogpt-Sync-Source'
PLAN_GROUP_PREFIX = 'plan-'
IRAN_MOBILE_RE = re.compile(r'^(?:\+98|98|0)?(9\d{9})$')

ALOGPT_AUTH_URL = os.getenv('ALOGPT_AUTH_URL', 'http://auth.localhost:8000').rstrip('/')
ALOGPT_SYNC_SECRET = os.getenv('ALOGPT_SYNC_SECRET', '').strip()


def secrets_match(provided: str, expected: str) -> bool:
    if not provided or not expected:
        return False
    left = hashlib.sha256(provided.encode('utf-8')).digest()
    right = hashlib.sha256(expected.encode('utf-8')).digest()
    return hmac.compare_digest(left, right)


def require_sync_secret(x_alogpt_sync_secret: str = Header(default='', alias=SYNC_HEADER)):
    if not secrets_match(x_alogpt_sync_secret, ALOGPT_SYNC_SECRET):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return True


def normalize_phone_number(raw: str | None) -> str | None:
    if not raw:
        return None
    cleaned = re.sub(r'[^\d+]', '', str(raw).strip())
    match = IRAN_MOBILE_RE.match(cleaned)
    if not match:
        return str(raw).strip() or None
    return f'+98{match.group(1)}'


def phone_from_user(user) -> str | None:
    oauth = getattr(user, 'oauth', None) or {}
    if isinstance(oauth, dict):
        for data in oauth.values():
            if isinstance(data, dict) and data.get('sub'):
                return normalize_phone_number(str(data['sub']))
    email = getattr(user, 'email', '') or ''
    if email.endswith('@phone.local'):
        return normalize_phone_number(email.split('@', 1)[0])
    return normalize_phone_number(email)


def phone_variants(phone: str) -> list[str]:
    normalized = normalize_phone_number(phone) or phone
    values = [normalized, normalized.lstrip('+')]
    unique = []
    for value in values:
        if value and value not in unique:
            unique.append(value)
    return unique


async def find_user_by_phone(phone: str, db: AsyncSession | None = None):
    for sub in phone_variants(phone):
        user = await Users.get_user_by_oauth_sub('oidc', sub, db=db)
        if user:
            return user
        user = await Users.get_user_by_email(f'{sub.lstrip("+")}@phone.local', db=db)
        if user:
            return user
    return None


async def sync_user_plan_group(user, plan: str, db: AsyncSession | None = None) -> bool:
    group_name = f'{PLAN_GROUP_PREFIX}{plan}'
    group = await Groups.get_group_by_name(group_name, db=db)
    if group is None:
        admin = await Users.get_super_admin_user(db=db)
        creator_id = admin.id if admin else user.id
        group = await Groups.insert_new_group(
            creator_id,
            GroupForm(
                name=group_name,
                description=f'اشتراک {plan}',
                data={'config': {'share': False}},
            ),
            db=db,
        )
        if group is None:
            log.error('Failed to create plan group %s', group_name)
            return False

    current_groups = await Groups.get_groups_by_member_id(user.id, db=db)
    for current in current_groups:
        if current.name.startswith(PLAN_GROUP_PREFIX) and current.name != group_name:
            await Groups.remove_users_from_group(current.id, [user.id], db=db)

    if not any(current.name == group_name for current in current_groups):
        await Groups.add_users_to_group(group.id, [user.id], db=db)
    return True


class DjangoAuthClient:
    def __init__(self, base_url: str | None = None, secret: str | None = None, timeout: int = 20):
        self.base_url = (base_url or ALOGPT_AUTH_URL).rstrip('/')
        self.secret = secret if secret is not None else ALOGPT_SYNC_SECRET
        self.timeout = timeout

    async def list_plans(self) -> list[dict]:
        return await self._request('GET', '/api/payments/plans/')

    async def current_plan(self, phone_number: str) -> dict:
        return await self._request('GET', '/api/payments/me/', params={'phone_number': phone_number})

    async def start_payment(self, phone_number: str, plan: str) -> dict:
        return await self._request(
            'POST',
            '/api/payments/start/',
            json={'phone_number': phone_number, 'plan': plan},
        )

    async def delete_user(self, phone_number: str) -> dict:
        return await self._request(
            'POST',
            '/api/payments/users/delete/',
            json={'phone_number': phone_number},
            extra_headers={SOURCE_HEADER: 'open-webui'},
        )

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
        extra_headers: dict | None = None,
    ):
        if not self.secret:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='همگام‌سازی با سرویس احراز هویت پیکربندی نشده است',
            )
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            SYNC_HEADER: self.secret,
        }
        if extra_headers:
            headers.update(extra_headers)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        try:
            async with aiohttp.ClientSession(trust_env=True) as session:
                async with session.request(
                    method,
                    f'{self.base_url}{path}',
                    json=json,
                    params=params,
                    headers=headers,
                    timeout=timeout,
                    ssl=AIOHTTP_CLIENT_SESSION_SSL,
                ) as response:
                    body = await response.json(content_type=None)
                    if response.status >= 400:
                        detail = body.get('detail') if isinstance(body, dict) else None
                        raise HTTPException(
                            status_code=response.status,
                            detail=detail or 'خطا در سرویس پرداخت',
                        )
                    return body
        except HTTPException:
            raise
        except Exception as exc:
            log.exception('Django auth request failed: %s %s', method, path)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail='ارتباط با سرویس پرداخت برقرار نشد',
            ) from exc


def schedule_django_user_delete(user) -> None:
    phone = phone_from_user(user)
    if not phone:
        log.warning('Cannot sync Django delete; no phone for user %s', getattr(user, 'id', None))
        return
    try:
        asyncio.create_task(_delete_django_user(phone))
    except RuntimeError:
        log.exception('Could not schedule Django user delete for %s', phone)


async def _delete_django_user(phone: str) -> None:
    try:
        await DjangoAuthClient().delete_user(phone)
    except Exception:
        log.exception('Failed to delete Django user %s', phone)
