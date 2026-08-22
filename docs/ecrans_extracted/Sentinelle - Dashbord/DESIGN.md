---
name: Sentinelle AIOps
colors:
  surface: '#101416'
  surface-dim: '#101416'
  surface-bright: '#363a3c'
  surface-container-lowest: '#0b0f11'
  surface-container-low: '#191c1e'
  surface-container: '#1d2022'
  surface-container-high: '#272a2d'
  surface-container-highest: '#323538'
  on-surface: '#e0e3e6'
  on-surface-variant: '#bdc9c3'
  inverse-surface: '#e0e3e6'
  inverse-on-surface: '#2d3133'
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
  tertiary: '#a7c8ff'
  on-tertiary: '#003060'
  tertiary-container: '#6d92cb'
  on-tertiary-container: '#002a54'
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
  tertiary-fixed: '#d5e3ff'
  tertiary-fixed-dim: '#a7c8ff'
  on-tertiary-fixed: '#001c3b'
  on-tertiary-fixed-variant: '#1d477c'
  background: '#101416'
  on-background: '#e0e3e6'
  surface-variant: '#323538'
typography:
  display:
    fontFamily: IBM Plex Sans
    fontSize: 40px
    fontWeight: '600'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: IBM Plex Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-md:
    fontFamily: IBM Plex Sans
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
  metric-xl:
    fontFamily: JetBrains Mono
    fontSize: 36px
    fontWeight: '600'
    lineHeight: 44px
  headline-lg-mobile:
    fontFamily: IBM Plex Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base_unit: 4px
  sidebar_width: 260px
  header_height: 64px
  gutter: 24px
  margin_mobile: 16px
  margin_desktop: 32px
---

## Brand & Style

The design system is engineered for the high-stakes environment of AIOps, where clarity, precision, and speed of interpretation are paramount. It adopts a **Corporate / Modern** aesthetic with a heavy emphasis on **systematic density**. 

The interface evokes an "Operational Command" feeling—authoritative and technical—without the visual clutter typical of legacy enterprise software. It prioritizes data-rich views through high-contrast typography and subtle structural layering. The style utilizes "Glassmorphism" sparingly for high-level overlays and "Tactile" cues for interactive states to guide the user's focus during critical incidents.

## Colors

This design system utilizes a dark-first hierarchy to reduce eye strain for operators monitoring screens for long durations. 

- **Primary & Secondary:** Used for action-oriented elements and branding. Teal-green represents growth and operational stability, while Cyan-blue signifies logic and technical depth.
- **Backgrounds:** A layered deep-sea palette. Use `#0B2545` for the core application canvas and `#13315C` for elevated containers or sidebars.
- **Semantic Status:** These colors are reserved strictly for system health. **Critical** alerts should employ a subtle outer glow using the status color at 20% opacity to draw attention without being abrasive.
- **Light Mode:** When toggled, the background transitions to a neutral off-white, using `#F2F4F7` for secondary surfaces to maintain depth perception.

## Typography

The typography strategy focuses on legibility and technical rigor. 

- **Headlines:** Use **IBM Plex Sans** to provide a structured, industrial feel. 
- **Body:** **Inter** is used for its exceptional readability in dense UI environments.
- **Data & Metrics:** All numerical data, timestamps, and status labels must use **JetBrains Mono**. The monospaced nature ensures that tabular data remains aligned during real-time updates, preventing "jitter" as numbers change.
- **Scale:** Keep body text at 14px (md) for standard enterprise density. Use 12px monospaced labels for metadata to maximize vertical space.

## Layout & Spacing

The layout follows a **Fluid Grid** model with a fixed left-rail navigation.

- **Grid:** Use a 12-column grid for the main content area. In dashboard views, prioritize a 3 or 4-column span for cards to maintain data density.
- **Rhythm:** All spacing is derived from a 4px base unit. 
- **Sidebar:** The navigation sidebar is fixed at 260px. On tablet, it collapses to a 64px icon-only rail.
- **Reflow:** On mobile, columns stack vertically. Cards should drop to 100% width, and horizontal padding reduces from 32px to 16px to maximize real estate for data tables.

## Elevation & Depth

Depth in this design system is communicated through **Tonal Layers** and **Low-Contrast Outlines** rather than heavy shadows.

- **Surface 0 (Background):** `#0B2545` - The primary app canvas.
- **Surface 1 (Cards/Sidebar):** `#13315C` - Elevated 1-step from the background.
- **Surface 2 (Modals/Popovers):** `#1C4476` - Use a subtle 1px border (`#FFFFFF` at 10% opacity) to define edges against Surface 1.
- **Borders:** Use soft, low-opacity dividers (`rgba(255, 255, 255, 0.08)`) to separate table rows and sidebar sections.
- **Interactions:** Hover states should slightly brighten the surface color or add a subtle inner glow rather than traditional drop shadows.

## Shapes

The shape language is "Rounded" to soften the technical nature of the platform, making it feel more modern and approachable.

- **Base Radius:** 8px (`0.5rem`) for standard buttons, input fields, and small cards.
- **Large Radius:** 16px (`1rem`) for primary dashboard containers and modals.
- **Pill:** Reserved exclusively for status badges and tags (e.g., "Healthy", "Critical") to distinguish them from interactive buttons.

## Components

- **Buttons:** Primary buttons use the Teal-green (`#1F8A70`) with white text. Ghost buttons use a 1px Cyan-blue border.
- **Data Cards:** Should feature a 16px padding. Headers within cards should use `label-sm` in all-caps for a "technical readout" look. Integrate micro-sparklines directly into the card header.
- **Status Badges:** Use the semantic status colors. For "Critical," add a pulse animation (0.5s duration, subtle opacity shift) to indicate real-time urgency.
- **Data Tables:** High-density with 8px vertical cell padding. Header rows should be pinned. Use alternating row stripes (zebra striping) with a very low opacity difference for readability.
- **Sidebar Navigation:** Use active state indicators (a 4px vertical bar on the left edge in Teal-green) to mark the current location.
- **Input Fields:** Deep navy background with a 1px border that glows Cyan-blue on focus. Labels should be `body-md` positioned above the input.