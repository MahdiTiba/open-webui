import logging

from fastapi import APIRouter, Depends, HTTPException, status
from open_webui.internal.db import get_async_session
from open_webui.models.auths import Auths
from open_webui.models.users import Users
from open_webui.socket.main import disconnect_user_sessions
from open_webui.utils.alogpt_sync import (
    DjangoAuthClient,
    find_user_by_phone,
    phone_from_user,
    require_sync_secret,
    sync_user_plan_group,
)
from open_webui.utils.auth import get_verified_user
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)

router = APIRouter()


class StartPaymentForm(BaseModel):
    plan: str


class PhoneForm(BaseModel):
    phone_number: str


class SyncPlanForm(BaseModel):
    phone_number: str
    plan: str


@router.get('/plans')
async def list_plans(user=Depends(get_verified_user)):
    return await DjangoAuthClient().list_plans()


@router.get('/me')
async def current_plan(user=Depends(get_verified_user)):
    phone = phone_from_user(user)
    if not phone:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='شماره موبایل کاربر یافت نشد')
    return await DjangoAuthClient().current_plan(phone)


@router.post('/start')
async def start_payment(form_data: StartPaymentForm, user=Depends(get_verified_user)):
    phone = phone_from_user(user)
    if not phone:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='شماره موبایل کاربر یافت نشد')
    return await DjangoAuthClient().start_payment(phone, form_data.plan)


@router.post('/internal/sync-plan')
async def sync_plan(
    form_data: SyncPlanForm,
    _: bool = Depends(require_sync_secret),
    db: AsyncSession = Depends(get_async_session),
):
    user = await find_user_by_phone(form_data.phone_number, db=db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='کاربر یافت نشد')
    ok = await sync_user_plan_group(user, form_data.plan, db=db)
    if not ok:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='همگام‌سازی گروه ناموفق بود')
    return {'detail': 'ok', 'plan': form_data.plan}


@router.post('/internal/users/delete')
async def delete_user(
    form_data: PhoneForm,
    _: bool = Depends(require_sync_secret),
    db: AsyncSession = Depends(get_async_session),
):
    user = await find_user_by_phone(form_data.phone_number, db=db)
    if user is None:
        return {'detail': 'not found'}
    first_user = await Users.get_first_user(db=db)
    if first_user and user.id == first_user.id:
        log.warning('Refusing to delete primary Open WebUI admin %s', user.id)
        return {'detail': 'primary admin skipped'}
    await Auths.delete_auth_by_id(user.id, db=db, sync_django=False)
    await disconnect_user_sessions(user.id)
    return {'detail': 'deleted'}
