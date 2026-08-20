<script lang="ts">
	import { showSidebar, WEBUI_NAME } from '$lib/stores';
	import Check from '$lib/components/icons/Check.svelte';

	const plans = [
		{
			id: 'free',
			name: 'رایگان',
			nameEn: 'Free',
			price: null,
			featured: false,
			features: [
				'مدل پایه',
				'تعداد محدود پیام‌ها و آپلودها',
				'امکان محدود ساخت تصویر',
				'حافظه محدود'
			]
		},
		{
			id: 'basic',
			name: 'پایه',
			nameEn: 'Basic',
			price: '۳۹۹/۰۰۰',
			featured: true,
			badge: 'پیشنهادی',
			features: [
				'مدل‌های پیشرفته',
				'ساخت تصویر پیشرفته همراه با Thinking',
				'حافظه گسترده‌تر در گفتگوهای مختلف',
				'قابلیت Deep Research گسترده‌تر'
			]
		},
		{
			id: 'plus',
			name: 'پلاس',
			nameEn: 'Plus',
			price: '۵۹۹/۰۰۰',
			featured: false,
			features: [
				'مدل پیشرفته Frontier Pro',
				'۵ یا ۲۰ برابر استفاده بیشتر نسبت به Basic',
				'چت نامحدود با مدل‌های پایه',
				'ساخت تصویر نامحدود و سریع‌تر',
				'حداکثر میزان حافظه و ظرفیت درک متن',
				'دسترسی زودهنگام به قابلیت‌های آزمایشی'
			]
		}
	];
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
					<header class="subscriptions-header text-center mb-10 sm:mb-12">
						<p class="subscriptions-kicker">AloGPT</p>
						<h1 class="subscriptions-title mt-2">اشتراک کاربری</h1>
						<p class="subscriptions-subtitle mt-3 mx-auto max-w-xl">
							طرح مناسب خود را انتخاب کنید و تجربه هوش مصنوعی را یک سطح بالاتر ببرید.
						</p>
					</header>

					<div class="grid grid-cols-1 lg:grid-cols-3 gap-5 lg:gap-6 items-stretch">
						{#each plans as plan, index}
							<article
								class="plan-card group relative flex flex-col rounded-2xl p-6 sm:p-7"
								class:plan-card--featured={plan.featured}
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
									{#if plan.price}
										<span class="plan-price-value">{plan.price}</span>
										<span class="plan-price-unit">تومان</span>
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

								<button type="button" class="plan-cta mt-8 w-full">
									{plan.featured ? 'شروع با طرح پایه' : `انتخاب ${plan.name}`}
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
		font-size: 0.75rem;
		letter-spacing: 0.28em;
		text-transform: uppercase;
		color: rgb(5 150 105);
		font-weight: 600;
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

	.plan-cta:hover {
		transform: translateY(-1px);
		background: rgba(16, 185, 129, 0.12);
		border-color: rgba(16, 185, 129, 0.3);
		color: rgb(4 120 87);
	}

	:global(.dark) .plan-cta:hover {
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

	.plan-card--featured .plan-cta:hover {
		background: linear-gradient(135deg, #047857, #059669);
		color: white;
		box-shadow: 0 16px 28px -12px rgba(16, 185, 129, 1);
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
