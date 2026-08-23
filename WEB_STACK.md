# Reusable web stack reference

## Simple landing page

Next.js or Vite, TypeScript, CSS/Tailwind, Motion only when interaction needs it.

## Premium marketing / storytelling

Next.js, TypeScript, Tailwind, GSAP + ScrollTrigger for scroll-linked timelines; add Lenis only when smooth scrolling is justified and reduced-motion behavior is handled.

## Dashboard / SaaS

Next.js, TypeScript, Tailwind, accessible component primitives, Recharts for conventional charts or ECharts for richer visualizations. Add Zod and React Hook Form only for real validation/form complexity.

## 3D experience

React Three Fiber + Drei only when 3D materially supports the experience. Budget mobile performance and provide a non-WebGL fallback.

## Quality gates

Use the project's package manager. Run lint, typecheck, build and relevant tests. Inspect mobile and desktop UI in a real browser when possible. Audit accessibility, performance, SEO metadata, bundle size and dependencies.

## Principles

Use native CSS before a library. Choose one animation system per responsibility. Prefer accessible, composable components. Do not install all listed libraries into every project.
