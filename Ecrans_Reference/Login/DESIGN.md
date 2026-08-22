---
name: Cyber-Sentinel Aesthetic
colors:
  surface: '#0b141c'
  surface-dim: '#0b141c'
  surface-bright: '#313a43'
  surface-container-lowest: '#060f16'
  surface-container-low: '#141c24'
  surface-container: '#182028'
  surface-container-high: '#222b33'
  surface-container-highest: '#2d363e'
  on-surface: '#dae3ee'
  on-surface-variant: '#b9cac2'
  inverse-surface: '#dae3ee'
  inverse-on-surface: '#29313a'
  outline: '#84948d'
  outline-variant: '#3a4a44'
  surface-tint: '#00e0b4'
  primary: '#c5ffe9'
  on-primary: '#00382b'
  primary-container: '#00f2c3'
  on-primary-container: '#006a54'
  inverse-primary: '#006b55'
  secondary: '#c3c6cf'
  on-secondary: '#2d3137'
  secondary-container: '#454950'
  on-secondary-container: '#b5b8c1'
  tertiary: '#eef2fd'
  on-tertiary: '#2c3138'
  tertiary-container: '#d2d6e0'
  on-tertiary-container: '#585d65'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#2effcf'
  primary-fixed-dim: '#00e0b4'
  on-primary-fixed: '#002118'
  on-primary-fixed-variant: '#00513f'
  secondary-fixed: '#dfe2eb'
  secondary-fixed-dim: '#c3c6cf'
  on-secondary-fixed: '#181c22'
  on-secondary-fixed-variant: '#43474e'
  tertiary-fixed: '#dee2ec'
  tertiary-fixed-dim: '#c2c7d0'
  on-tertiary-fixed: '#171c23'
  on-tertiary-fixed-variant: '#42474f'
  background: '#0b141c'
  on-background: '#dae3ee'
  surface-variant: '#2d363e'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  title-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  label-mono:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: '1.2'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 16px
  margin-page: 24px
  container-padding: 20px
  sidebar-width: 260px
---

## Brand & Style

This design system is built for the high-stakes world of AIOps—Infrastructure monitoring, predictive analysis, and automated security. The personality is authoritative, vigilant, and technologically advanced. It is designed to evoke a sense of "Mission Control" where complex data is distilled into actionable, AI-driven insights.

The visual style is **Corporate Modern with Cyber-Technical influences**. It utilizes a deep-space palette to reduce eye strain during long monitoring sessions, punctuated by vibrant neon "energy" points that represent AI activity and system health. The aesthetic leans into high-precision layouts, subtle glassmorphism for layered intelligence, and glowing accents to guide the user's focus toward critical events.

## Colors

The palette is strictly dark-mode centric to maintain a professional, developer-focused environment.

- **Primary (#00F2C3):** A neon "Electric Teal" used for primary actions, success states, and AI-driven elements. It should be used sparingly to maintain high impact.
- **Surface Layering:** 
    - **Background (#0D1117):** The deepest base layer.
    - **Container (#161B22):** Used for cards and sidebar navigation to create subtle depth.
    - **Glass Layer (RGBA 22, 27, 34, 0.7):** Used for floating panels with a 12px backdrop blur.
- **Accents:** Neon glows and gradients are used to signify "active" AI processing.
- **Semantics:** Red (#FF7B72) for critical alerts, Orange (#D29922) for warnings, and Blue (#58A6FF) for information.

## Typography

The typography system prioritizes legibility and technical precision.

- **Primary Sans (Inter):** Used for all UI controls, headings, and body copy. It provides a clean, modern look that balances the "tech" aesthetic with readability.
- **Technical Mono (JetBrains Mono):** Used specifically for server names, IDs, timestamps, and data tables. This reinforces the "AIOps" and developer-centric nature of the platform.
- **Scale:** Headings use tighter letter-spacing to feel more "dense" and authoritative, while technical labels use slightly increased spacing for clarity in data-heavy views.

## Layout & Spacing

The layout utilizes a **Fixed Sidebar + Fluid Content** model. 

- **Grid:** A 12-column system is used for dashboard layouts, transitioning to a single-column focused view for the AI Assistant interface.
- **Sidebar:** Fixed at 260px. It uses a deeper background than the main content area to anchor the navigation.
- **Rhythm:** A 4px baseline grid ensures tight, technical alignment. Components generally use 16px or 20px internal padding to maintain a spacious but professional density.
- **AI Chat Layout:** Specifically centered with a maximum width of 900px to ensure conversational readability, while monitoring dashboards expand to 100% of the viewport width.

## Elevation & Depth

This design system avoids traditional drop shadows in favor of **Tonal Elevation and Glows**.

- **Z-Index 0 (Base):** #0D1117 (The canvas).
- **Z-Index 1 (Cards/Sidebar):** #161B22 with a 1px solid border of #30363D.
- **Z-Index 2 (Popovers/Modals):** Glassmorphism effect—Semi-transparent #161B22 (70% opacity) with a 12px backdrop-blur and a subtle teal inner-glow (1px stroke at 10% opacity).
- **AI Focus:** Elements actively being analyzed by the AI receive a `0px 0px 15px` outer glow using the primary teal color at 15% opacity.

## Shapes

The shape language is **Soft-Geometric**. 

- **Standard Radius:** 4px (Soft) for most technical components like input fields, small buttons, and data cells.
- **Container Radius:** 8px (Large) for cards and main UI containers.
- **Interactive Radius:** Buttons and chips use a consistent 6px radius to feel distinct from data containers.
- **Iconography:** Icons should follow a 2px stroke weight with slight rounding on corners to match the UI's "refined tech" look.

## Components

- **Buttons:**
    - **Primary:** Solid Teal (#00F2C3) with dark text. High visibility.
    - **Ghost/Secondary:** Transparent background with teal border and text. Used for less urgent actions.
- **AI Assistant Input:** A large, persistent footer bar with glassmorphism. It includes a "Prompt" area and quick-action chips above it.
- **Data Tables:** High-density, borderless rows. Use #161B22 for header backgrounds. Highlight "Critical" rows with a 2px left-border in alert red.
- **Status Chips:** Small, condensed pills. They use a background color at 10% opacity of the status color (e.g., green for 'active') with high-contrast text.
- **Cards:** Use #161B22 as the base. Titles should be in Inter Bold 14px, and content should use JetBrains Mono for data points.
- **Glowing Pulse:** A small teal dot with a CSS pulse animation is used next to "Live" monitoring feeds to indicate real-time connectivity.