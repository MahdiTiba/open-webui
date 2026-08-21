import { WEBUI_API_BASE_URL } from '$lib/constants';

const jsonHeaders = (token: string) => ({
	Accept: 'application/json',
	'Content-Type': 'application/json',
	Authorization: `Bearer ${token}`
});

const parseResponse = async (res: Response) => {
	const body = await res.json().catch(() => ({}));
	if (!res.ok) {
		throw body?.detail || 'خطای پرداخت';
	}
	return body;
};

export const getPaymentPlans = async (token: string) => {
	const res = await fetch(`${WEBUI_API_BASE_URL}/payments/plans`, {
		method: 'GET',
		headers: jsonHeaders(token),
		credentials: 'include'
	});
	return parseResponse(res);
};

export const getCurrentPlan = async (token: string) => {
	const res = await fetch(`${WEBUI_API_BASE_URL}/payments/me`, {
		method: 'GET',
		headers: jsonHeaders(token),
		credentials: 'include'
	});
	return parseResponse(res);
};

export const startPayment = async (token: string, plan: string) => {
	const res = await fetch(`${WEBUI_API_BASE_URL}/payments/start`, {
		method: 'POST',
		headers: jsonHeaders(token),
		credentials: 'include',
		body: JSON.stringify({ plan })
	});
	return parseResponse(res);
};
