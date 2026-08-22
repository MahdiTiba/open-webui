<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { toast } from 'svelte-sonner';
	import { showSidebar, setUserPlan, user, WEBUI_NAME } from '$lib/stores';
	import { getSessionUser } from '$lib/apis/auths';
	import { getCurrentPlan, getPaymentPlans, startPayment } from '$lib/apis/payments';
	import Check from '$lib/components/icons/Check.svelte';
	import Modal from '$lib/components/common/Modal.svelte';

	type PlanId = 'free' | 'basic' | 'plus' | 'pro' | 'enterprise';

	const PLAN_RANK: Record<PlanId, number> = {
		free: 0,
		basic: 1,
		plus: 2,
		pro: 3,
		enterprise: 4
	};

	const planCopy: Record<
		PlanId,
		{ name: string; nameEn: string; featured?: boolean; badge?: string; features: string[] }
	> = {
		free: {
			name: 'رایگان',
			nameEn: 'Free',
			features: ['مدل پایه', 'تعداد محدود پیام‌ها و آپلودها', 'امکان محدود ساخت تصویر', 'حافظه محدود']
		},
		basic: {
			name: 'پایه',
			nameEn: 'Basic',
			featured: true,
			badge: 'پیشنهادی',
			features: [
				'مدل‌های پیشرفته',
				'ساخت تصویر پیشرفته همراه با Thinking',
				'حافظه گسترده‌تر در گفتگوهای مختلف',
				'قابلیت Deep Research گسترده‌تر'
			]
		},
		plus: {
			name: 'پلاس',
			nameEn: 'Plus',
			features: [
				'مدل پیشرفته Frontier Pro',
				'۵ یا ۲۰ برابر استفاده بیشتر نسبت به Basic',
				'چت نامحدود با مدل‌های پایه',
				'ساخت تصویر نامحدود و سریع‌تر',
				'حداکثر میزان حافظه و ظرفیت درک متن',
				'دسترسی زودهنگام به قابلیت‌های آزمایشی'
			]
		},
		pro: {
			name: 'پرو',
			nameEn: 'Pro',
			features: ['همه امکانات پلاس', 'اولویت در پردازش', 'پشتیبانی اختصاصی']
		},
		enterprise: {
			name: 'سازمانی',
			nameEn: 'Enterprise',
			features: ['همه امکانات پرو', 'مدیریت تیمی', 'توافق سطح خدمات']
		}
	};

	let plans: Array<{
		id: PlanId;
		name: string;
		nameEn: string;
		amount: number | null;
		currency: string;
		purchasable: boolean;
		featured: boolean;
		badge?: string;
		features: string[];
	}> = (['free', 'basic', 'plus'] as PlanId[]).map((id) => ({
		id,
		...planCopy[id],
		amount: null,
		currency: 'IRT',
		purchasable: false,
		featured: Boolean(planCopy[id].featured)
	}));

	let currentPlan = 'free';
	let payingPlan: string | null = null;
	let resultOpen = false;
	let resultSuccess = false;
	let resultPlan = '';
	let resultPlanName = '';
	let resultConsumed = false;

	const planLabel = (id: string) => planCopy[id as PlanId]?.name || id;

	const planRank = (id: string) => PLAN_RANK[id as PlanId] ?? 0;

	const isLowerPlan = (planId: PlanId, activePlan: string) =>
		planRank(planId) < planRank(activePlan);

	const isPlanDisabled = (
		plan: { id: PlanId; purchasable: boolean },
		activePlan: string,
		busyPlan: string | null
	) =>
		plan.id === activePlan ||
		busyPlan !== null ||
		plan.id === 'free' ||
		!plan.purchasable ||
		isLowerPlan(plan.id, activePlan);

	const formatAmount = (amount: number | null, currency: string) => {
		if (amount === null || amount === undefined) return '';
		const formatted = new Intl.NumberFormat('fa-IR').format(amount);
		return currency === 'IRR' ? `${formatted} ریال` : formatted;
	};

	const applyCatalog = (catalog: any[]) => {
		if (!Array.isArray(catalog) || catalog.length === 0) return;
		const order: PlanId[] = ['free', 'basic', 'plus', 'pro', 'enterprise'];
		plans = order
			.map((id) => catalog.find((item) => item.id === id))
			.filter(Boolean)
			.filter((item) => item?.id === 'free' || item?.purchasable || Number(item?.amount || 0) > 0)
			.map((item) => {
				const copy = planCopy[item.id as PlanId] || {
					name: item.name,
					nameEn: item.id,
					features: []
				};
				return {
					id: item.id as PlanId,
					name: copy.name || item.name,
					nameEn: copy.nameEn || item.id,
					amount: item.id === 'free' ? null : Number(item.amount || 0),
					currency: item.currency || 'IRT',
					purchasable: Boolean(item.purchasable),
					featured: Boolean(copy.featured),
					badge: copy.badge,
					features: copy.features
				};
			});
	};

	const loadBilling = async () => {
		const token = localStorage.token;
		if (!token) return;
		try {
			const [catalog, me] = await Promise.all([getPaymentPlans(token), getCurrentPlan(token)]);
			applyCatalog(catalog);
			if (me?.plan) currentPlan = setUserPlan(me.plan, me.plan_name);
		} catch (error) {
			toast.error(typeof error === 'string' ? error : 'بارگذاری طرح‌ها ناموفق بود');
		}
	};

	const openResultFromQuery = async () => {
		const params = $page.url.searchParams;
		const payment = params.get('payment');
		if (payment !== 'success' && payment !== 'failed') return;
		resultSuccess = payment === 'success';
		resultPlan = params.get('plan') || '';
		resultPlanName = planLabel(resultPlan);
		resultOpen = true;
		if (resultSuccess) {
			currentPlan = setUserPlan(resultPlan || currentPlan);
			try {
				const sessionUser = await getSessionUser(localStorage.token);
				if (sessionUser) await user.set(sessionUser);
			} catch {
				/* session refresh is best-effort */
			}
		}
	};

	const closeResult = async () => {
		if (resultConsumed) return;
		resultConsumed = true;
		resultOpen = false;
		if (resultSuccess) {
			await goto('/');
			return;
		}
		await goto('/subscriptions', { replaceState: true });
	};

	$: if (!resultOpen && resultPlan && !resultConsumed) {
		void closeResult();
	}

	const pay = async (planId: PlanId, purchasable: boolean) => {
		if (planId === currentPlan || payingPlan || isLowerPlan(planId, currentPlan)) return;
		if (!purchasable) return;
		payingPlan = planId;
		try {
			const result = await startPayment(localStorage.token, planId);
			if (!result?.payment_url) {
				throw 'آدرس درگاه دریافت نشد';
			}
			window.location.assign(result.payment_url);
		} catch (error) {
			payingPlan = null;
			toast.error(typeof error === 'string' ? error : 'شروع پرداخت ناموفق بود');
		}
	};

	const ctaLabel = (
		plan: { id: PlanId; featured?: boolean; purchasable: boolean },
		activePlan: string,
		busyPlan: string | null
	) => {
		if (busyPlan === plan.id) return 'در حال انتقال به درگاه...';
		if (plan.id === activePlan) return 'پلن فعلی';
		if (plan.id === 'free') return `انتخاب ${planCopy.free.name}`;
		if (!plan.purchasable) return 'به‌زودی';
		return plan.featured ? 'شروع با طرح پایه' : `پرداخت ${planCopy[plan.id].name}`;
	};

	onMount(async () => {
		await loadBilling();
		await openResultFromQuery();
	});
</script>

<svelte:head>
	<title>اشتراک کاربری | {$WEBUI_NAME}</title>
</svelte:head>

<div
	class="subscriptions-page flex flex-col w-full h-screen max-h-[100dvh] transition-width duration-200 ease-in-out {$showSidebar
		? 'md:max-w-[calc(100%-var(--sidebar-width))]'
		: ''} max-w-full"
	dir="rtl"
>
	<div class="flex-1 overflow-y-auto">
		<div class="subscriptions-shell relative min-h-full flex flex-col">
			<div class="subscriptions-atmosphere" aria-hidden="true"></div>

			<div
				class="relative z-10 flex-1 flex flex-col justify-center px-4 sm:px-6 lg:px-10 py-10 sm:py-14"
			>
				<div class="mx-auto w-full max-w-6xl">
					<div class="mb-6">
						<a href="/" class="subscriptions-back">بازگشت</a>
					</div>
					<header class="subscriptions-header text-center mb-10 sm:mb-12">
						<img
							src="/static/login_logo.png"
							alt=""
							width="240"
							height="80"
							class="subscriptions-logo"
						/>
						<p class="subscriptions-kicker">aloGPT</p>
						<h1 class="subscriptions-title mt-2">
							اشتراک کاربری ({planLabel(currentPlan)})
						</h1>
						<p class="subscriptions-subtitle mt-3 mx-auto max-w-xl">
							طرح مناسب خود را انتخاب کنید و تجربه هوش مصنوعی را یک سطح بالاتر ببرید.
						</p>
					</header>

					<div class="grid grid-cols-1 lg:grid-cols-3 gap-5 lg:gap-6 items-stretch">
						{#each plans as plan, index}
							<article
								class="plan-card group relative flex flex-col rounded-2xl p-6 sm:p-7"
								class:plan-card--featured={plan.featured}
								class:plan-card--current={plan.id === currentPlan}
								style="--delay: {index * 80}ms"
							>
								{#if plan.badge}
									<div class="plan-badge">{plan.badge}</div>
								{/if}

								<div class="flex items-baseline justify-between gap-3">
									<div>
										<h2 class="plan-name">{plan.name}</h2>
										<p class="plan-name-en">{plan.nameEn}</p>
									</div>
								</div>

								<div class="plan-price mt-6">
									{#if plan.amount}
										<span class="plan-price-value">{formatAmount(plan.amount, plan.currency)}</span>
										{#if plan.currency !== 'IRR'}
											<span class="plan-price-unit">تومان</span>
										{/if}
										<span class="plan-price-period">/ ماه</span>
									{:else}
										<span class="plan-price-value">رایگان</span>
									{/if}
								</div>

								<ul class="mt-7 space-y-3.5 flex-1">
									{#each plan.features as feature}
										<li class="flex items-start gap-2.5 text-[13.5px] leading-6">
											<span class="plan-check mt-0.5 shrink-0">
												<Check className="size-3.5" strokeWidth="2" />
											</span>
											<span class="plan-feature">{feature}</span>
										</li>
									{/each}
								</ul>

								<button
									type="button"
									class="plan-cta mt-8 w-full"
									disabled={isPlanDisabled(plan, currentPlan, payingPlan)}
									on:click={() => pay(plan.id, plan.purchasable)}
								>
									{ctaLabel(plan, currentPlan, payingPlan)}
								</button>
							</article>
						{/each}
					</div>
				</div>
			</div>

			<footer class="relative z-10 flex justify-center pb-8 pt-2">
				{@html `<a referrerpolicy='origin' target='_blank' href='https://trustseal.enamad.ir/?id=774452&Code=ht1hpnAHsgAfvu3KDvjHVrwQDCT5vUQ8'><img referrerpolicy='origin' src='https://trustseal.enamad.ir/logo.aspx?id=774452&Code=ht1hpnAHsgAfvu3KDvjHVrwQDCT5vUQ8' alt='' style='cursor:pointer' code='ht1hpnAHsgAfvu3KDvjHVrwQDCT5vUQ8'></a>`}
			</footer>
		</div>
	</div>
</div>

<Modal bind:show={resultOpen} size="xs" className="bg-white dark:bg-gray-900 rounded-2xl">
	<div class="p-6 text-center" dir="rtl">
		<div
			class="mx-auto mb-4 flex size-12 items-center justify-center rounded-full {resultSuccess
				? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-300'
				: 'bg-rose-500/15 text-rose-600 dark:text-rose-300'}"
		>
			{#if resultSuccess}
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					class="size-6"
				>
					<path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round" />
				</svg>
			{:else}
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					class="size-6"
				>
					<path d="M6 6l12 12M18 6L6 18" stroke-linecap="round" stroke-linejoin="round" />
				</svg>
			{/if}
		</div>
		<h2 class="text-lg font-bold text-gray-900 dark:text-gray-50">
			{resultSuccess ? 'پرداخت موفق' : 'پرداخت ناموفق'}
		</h2>
		<p class="mt-2 text-sm leading-6 text-gray-600 dark:text-gray-300">
			{#if resultSuccess}
				اشتراک «{resultPlanName}» برای شما فعال شد.
			{:else}
				پرداخت انجام نشد و طرح فعلی شما تغییر نکرد.
			{/if}
		</p>
		<button type="button" class="plan-cta mt-6 w-full" on:click={closeResult}>تایید</button>
	</div>
</Modal>

<style>
	.subscriptions-shell {
		background:
			radial-gradient(1200px 500px at 50% -10%, rgba(16, 185, 129, 0.12), transparent 60%),
			radial-gradient(800px 400px at 100% 20%, rgba(59, 130, 246, 0.06), transparent 55%),
			radial-gradient(700px 360px at 0% 30%, rgba(16, 185, 129, 0.05), transparent 50%);
	}

	:global(.dark) .subscriptions-shell {
		background:
			radial-gradient(1200px 500px at 50% -10%, rgba(16, 185, 129, 0.14), transparent 60%),
			radial-gradient(800px 400px at 90% 15%, rgba(56, 189, 248, 0.07), transparent 55%),
			radial-gradient(700px 360px at 10% 40%, rgba(16, 185, 129, 0.06), transparent 50%);
	}

	.subscriptions-atmosphere {
		pointer-events: none;
		position: absolute;
		inset: 0;
		background-image: linear-gradient(
			to bottom,
			transparent,
			rgba(0, 0, 0, 0.015) 50%,
			transparent
		);
		mask-image: radial-gradient(ellipse at center, black 30%, transparent 75%);
	}

	.subscriptions-kicker {
		font-size: 0.95rem;
		letter-spacing: 0.18em;
		text-transform: none;
		color: rgb(5 150 105);
		font-weight: 650;
		margin-top: 0.85rem;
	}

	:global(.dark) .subscriptions-kicker {
		color: rgb(110 231 183);
	}

	.subscriptions-title {
		font-size: clamp(1.75rem, 3vw, 2.35rem);
		font-weight: 700;
		letter-spacing: -0.02em;
		color: rgb(17 24 39);
	}

	:global(.dark) .subscriptions-title {
		color: rgb(243 244 246);
	}

	.subscriptions-subtitle {
		font-size: 0.95rem;
		line-height: 1.7;
		color: rgb(107 114 128);
	}

	:global(.dark) .subscriptions-subtitle {
		color: rgb(156 163 175);
	}

	.subscriptions-header {
		animation: rise 560ms cubic-bezier(0.22, 1, 0.36, 1) both;
	}

	.subscriptions-logo {
		display: block;
		margin: 0 auto;
		height: 80px;
		width: auto;
		max-width: 240px;
		object-fit: contain;
		border-radius: 1.1rem;
	}

	.subscriptions-back {
		display: inline-flex;
		align-items: center;
		font-size: 0.875rem;
		font-weight: 600;
		color: rgb(55 65 81);
		padding: 0.45rem 0.9rem;
		border-radius: 0.75rem;
		border: 1px solid rgba(17, 24, 39, 0.08);
		background: rgba(255, 255, 255, 0.7);
		text-decoration: none;
	}

	.subscriptions-back:hover {
		border-color: rgba(16, 185, 129, 0.28);
		color: rgb(4 120 87);
		background: rgba(16, 185, 129, 0.08);
	}

	:global(.dark) .subscriptions-back {
		color: rgb(229 231 235);
		border-color: rgba(255, 255, 255, 0.08);
		background: rgba(255, 255, 255, 0.04);
	}

	:global(.dark) .subscriptions-back:hover {
		border-color: rgba(52, 211, 153, 0.32);
		color: rgb(167 243 208);
		background: rgba(16, 185, 129, 0.12);
	}

	.plan-card {
		background: rgba(255, 255, 255, 0.78);
		border: 1px solid rgba(17, 24, 39, 0.08);
		backdrop-filter: blur(10px);
		box-shadow:
			0 1px 0 rgba(255, 255, 255, 0.5) inset,
			0 18px 40px -28px rgba(15, 23, 42, 0.35);
		transition:
			transform 280ms cubic-bezier(0.22, 1, 0.36, 1),
			border-color 220ms ease,
			box-shadow 280ms ease;
		animation: rise 640ms cubic-bezier(0.22, 1, 0.36, 1) both;
		animation-delay: var(--delay);
	}

	:global(.dark) .plan-card {
		background: rgba(17, 17, 17, 0.72);
		border-color: rgba(255, 255, 255, 0.08);
		box-shadow:
			0 1px 0 rgba(255, 255, 255, 0.04) inset,
			0 22px 44px -28px rgba(0, 0, 0, 0.8);
	}

	.plan-card:hover {
		transform: translateY(-4px);
		border-color: rgba(16, 185, 129, 0.35);
		box-shadow:
			0 1px 0 rgba(255, 255, 255, 0.55) inset,
			0 24px 50px -24px rgba(16, 185, 129, 0.35);
	}

	:global(.dark) .plan-card:hover {
		border-color: rgba(52, 211, 153, 0.35);
		box-shadow:
			0 1px 0 rgba(255, 255, 255, 0.05) inset,
			0 28px 56px -24px rgba(16, 185, 129, 0.28);
	}

	.plan-card--featured {
		border-color: rgba(16, 185, 129, 0.45);
		background:
			linear-gradient(180deg, rgba(16, 185, 129, 0.1), transparent 42%),
			rgba(255, 255, 255, 0.88);
		transform: scale(1.02);
		z-index: 1;
	}

	:global(.dark) .plan-card--featured {
		border-color: rgba(52, 211, 153, 0.4);
		background:
			linear-gradient(180deg, rgba(16, 185, 129, 0.16), transparent 45%),
			rgba(17, 17, 17, 0.86);
	}

	.plan-card--featured:hover {
		transform: scale(1.02) translateY(-4px);
	}

	.plan-badge {
		position: absolute;
		top: -0.7rem;
		left: 50%;
		transform: translateX(-50%);
		padding: 0.28rem 0.8rem;
		border-radius: 999px;
		font-size: 0.7rem;
		font-weight: 600;
		letter-spacing: 0.02em;
		color: white;
		background: linear-gradient(135deg, #059669, #10b981);
		box-shadow: 0 8px 18px -10px rgba(16, 185, 129, 0.9);
		white-space: nowrap;
	}

	.plan-name {
		font-size: 1.35rem;
		font-weight: 700;
		color: rgb(17 24 39);
		letter-spacing: -0.01em;
	}

	:global(.dark) .plan-name {
		color: rgb(249 250 251);
	}

	.plan-name-en {
		margin-top: 0.15rem;
		font-size: 0.75rem;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: rgb(156 163 175);
		font-weight: 500;
	}

	.plan-price-value {
		font-size: 1.85rem;
		font-weight: 700;
		letter-spacing: -0.03em;
		color: rgb(17 24 39);
		font-variant-numeric: tabular-nums;
	}

	:global(.dark) .plan-price-value {
		color: rgb(249 250 251);
	}

	.plan-price-unit {
		margin-right: 0.35rem;
		font-size: 0.95rem;
		font-weight: 600;
		color: rgb(55 65 81);
	}

	:global(.dark) .plan-price-unit {
		color: rgb(209 213 219);
	}

	.plan-price-period {
		margin-right: 0.25rem;
		font-size: 0.8rem;
		color: rgb(156 163 175);
	}

	.plan-check {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 1.2rem;
		height: 1.2rem;
		border-radius: 999px;
		background: rgba(16, 185, 129, 0.12);
		color: rgb(5 150 105);
	}

	:global(.dark) .plan-check {
		background: rgba(16, 185, 129, 0.18);
		color: rgb(110 231 183);
	}

	.plan-feature {
		color: rgb(55 65 81);
	}

	:global(.dark) .plan-feature {
		color: rgb(209 213 219);
	}

	.plan-cta {
		border-radius: 0.9rem;
		padding: 0.8rem 1rem;
		font-size: 0.875rem;
		font-weight: 600;
		transition:
			background 180ms ease,
			color 180ms ease,
			transform 180ms ease,
			box-shadow 180ms ease;
		background: rgba(17, 24, 39, 0.04);
		color: rgb(17 24 39);
		border: 1px solid rgba(17, 24, 39, 0.08);
	}

	:global(.dark) .plan-cta {
		background: rgba(255, 255, 255, 0.04);
		color: rgb(243 244 246);
		border-color: rgba(255, 255, 255, 0.08);
	}

	.plan-cta:hover:not(:disabled) {
		transform: translateY(-1px);
		background: rgba(16, 185, 129, 0.12);
		border-color: rgba(16, 185, 129, 0.3);
		color: rgb(4 120 87);
	}

	:global(.dark) .plan-cta:hover:not(:disabled) {
		background: rgba(16, 185, 129, 0.16);
		border-color: rgba(52, 211, 153, 0.35);
		color: rgb(167 243 208);
	}

	.plan-card--featured .plan-cta {
		background: linear-gradient(135deg, #059669, #10b981);
		border-color: transparent;
		color: white;
		box-shadow: 0 12px 24px -14px rgba(16, 185, 129, 0.95);
	}

	.plan-card--featured .plan-cta:hover:not(:disabled) {
		background: linear-gradient(135deg, #047857, #059669);
		color: white;
		box-shadow: 0 16px 28px -12px rgba(16, 185, 129, 1);
	}

	.plan-cta:disabled {
		cursor: default;
		opacity: 0.7;
		transform: none;
		box-shadow: none;
	}

	@keyframes rise {
		from {
			opacity: 0;
			transform: translateY(16px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@media (max-width: 1023px) {
		.plan-card--featured {
			transform: none;
		}

		.plan-card--featured:hover {
			transform: translateY(-4px);
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.subscriptions-header,
		.plan-card {
			animation: none;
		}

		.plan-card,
		.plan-cta {
			transition: none;
		}
	}
</style>
