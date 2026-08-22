---
name: Sentinelle AIOps
colors:
  surface: '#0f1412'
  surface-dim: '#0f1412'
  surface-bright: '#353a38'
  surface-container-lowest: '#0a0f0d'
  surface-container-low: '#181d1b'
  surface-container: '#1c211e'
  surface-container-high: '#262b29'
  surface-container-highest: '#313633'
  on-surface: '#dfe4e0'
  on-surface-variant: '#bdc9c3'
  inverse-surface: '#dfe4e0'
  inverse-on-surface: '#2c322f'
  outline: '#87938e'
  outline-variant: '#3e4945'
  surface-tint: '#78d8ba'
  primary: '#78d8ba'
  on-primary: '#00382b'
  primary-container: '#3da186'
  on-primary-container: '#003025'
  inverse-primary: '#006b55'
  secondary: '#81d0f8'
  on-secondary: '#003548'
  secondary-container: '#017094'
  on-secondary-container: '#ceedff'
  tertiary: '#ffb4a7'
  on-tertiary: '#5a1a12'
  tertiary-container: '#d37768'
  on-tertiary-container: '#51140c'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#94f5d6'
  primary-fixed-dim: '#78d8ba'
  on-primary-fixed: '#002018'
  on-primary-fixed-variant: '#005140'
  secondary-fixed: '#c1e8ff'
  secondary-fixed-dim: '#81d0f8'
  on-secondary-fixed: '#001e2b'
  on-secondary-fixed-variant: '#004d67'
  tertiary-fixed: '#ffdad4'
  tertiary-fixed-dim: '#ffb4a7'
  on-tertiary-fixed: '#3d0502'
  on-tertiary-fixed-variant: '#783025'
  background: '#0f1412'
  on-background: '#dfe4e0'
  surface-variant: '#313633'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  display-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  data-mono:
    fontFamily: IBM Plex Sans
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  sidebar-width: 240px
  header-height: 56px
---

## Brand & Style
The design system is engineered for high-performance monitoring and observability. It targets DevOps engineers and SREs who require immediate clarity amidst high-volume data. The aesthetic is **Corporate Modern** with a **Technical** edge, prioritizing information density without sacrificing legibility. 

The visual language draws inspiration from terminal interfaces and laboratory instrumentation—precise, reliable, and calm. It avoids unnecessary decoration, using structural lines and purposeful color coding to guide the eye toward anomalies and system health metrics. The interface feels like a sophisticated mission control center: dark-mode first to reduce eye strain during long shifts, with high-contrast accents for critical alerts.

## Colors
The palette is anchored in deep, receding blues to create a stable environment for data visualization. 
- **Primary Teal (#1F8A70):** Used for primary actions, active navigation states, and "optimal" system paths.
- **Secondary Cyan (#2E86AB):** Employed for informational accents, secondary buttons, and data series in charts.
- **Background Tiers:** The base background uses the darkest navy (#0B2545), while cards and elevated surfaces use the steel blue (#13315C) to create subtle depth.
- **Semantic Status:** Traffic-light colors are calibrated for high visibility against the dark background, ensuring critical alerts are never missed.

## Typography
The system uses **Inter** for the majority of the UI to ensure maximum readability and a clean, modern feel. For metrics, logs, and technical data points, **IBM Plex Sans** is utilized to leverage its superior legibility and tabular numerals, ensuring that columns of numbers align perfectly for quick scanning.

- **Data Density:** Use `body-sm` for secondary metadata and `data-mono` for all variable system outputs.
- **Hierarchy:** Use `label-caps` for section headers within sidebars and small card titles to maintain structure without taking up excessive vertical space.

## Layout & Spacing
The layout follows a **Fluid Grid** model with a sidebar-and-topbar shell. 
- **Sidebar:** Fixed at 240px. Collapsible to 64px (icon-only) for increased dashboard real estate.
- **Grid:** Use a 12-column layout for dashboard views. Gutters are fixed at 16px to maintain high data density.
- **Rhythm:** Spacing follows a 4px baseline. Components use 12px or 16px internal padding (SM/MD) to ensure the UI feels "breathable" despite the high volume of information.
- **Mobile:** On small screens, the sidebar transitions to a bottom navigation bar or a hidden drawer, and dashboard cards stack vertically.

## Elevation & Depth
In this dark-mode environment, depth is communicated through **Tonal Layering** and **Low-contrast Outlines** rather than heavy shadows.
- **Level 0 (Base):** #0B2545 (The canvas).
- **Level 1 (Cards/Sidebar):** #13315C with a 1px border of #FFFFFF (10% opacity).
- **Level 2 (Modals/Popovers):** #1C3D6E with a subtle 8px blur shadow (Black, 40% opacity).
- **Dividers:** Use 1px solid lines with 10% white opacity to separate rows in data tables and sections in sidebars.

## Shapes
The design system employs a **Rounded** (Level 2) shape language to soften the technical nature of the platform.
- **Standard Radius:** 8px for buttons, input fields, and small widgets.
- **Large Radius:** 12px or 16px (rounded-lg/xl) for primary dashboard containers and cards.
- **Interactive Elements:** Active states should be clearly defined by a 2px outer stroke in the primary teal color.

## Components
- **Buttons:** Primary buttons use the Teal-green (#1F8A70) with white text. Ghost buttons use the Cyan-blue (#2E86AB) for outlines. 
- **Status Badges:** Compact pills with a low-opacity background of the status color and a high-opacity text/icon foreground (e.g., 15% Green BG, 100% Green text).
- **Data Cards:** Containers with 24px padding. Titles are `headline-sm`. Charts should utilize a color palette derived from the Primary and Secondary accents, with a grey #8E9AAF used for grid lines.
- **AI Chat Assistant:** A persistent floating action button in the bottom right, opening a 360px wide drawer. Use a subtle glassmorphism effect (backdrop-filter: blur(10px)) for the chat input area to distinguish it from static data.
- **Global Search:** Located in the top bar, utilizing a "Cmd+K" pattern. Full-width on focus with an overlay mask on the content below.
- **Navigation Sidebar:** High-contrast icons (20px) with 12px spacing from text. The active state includes a 3px vertical "indicator" on the left edge in Teal-green.