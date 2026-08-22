# Prompt Stitch — Plateforme AIOps

Copie-colle le bloc ci-dessous dans Stitch. Tu peux l'envoyer en une fois pour générer
une première vue d'ensemble, puis réutiliser les sections "ÉCRAN" une par une pour
affiner chaque page individuellement.

---

## PROMPT PRINCIPAL

Design a professional, enterprise-grade web dashboard application called **" Sentinelle AIOps
Platform"** — a centralized IT operations platform that unifies predictive monitoring,
cybersecurity anomaly detection, network automation (NetDevOps), IT asset inventory,
and AI-powered reporting for system and network administrators.

**Product context:** This is a B2B technical/ops tool used by network administrators,
security technicians, and IT managers to monitor servers and network equipment (Cisco
switches/routers), detect intrusions, predict hardware failures before they happen, audit
network configurations against security benchmarks, and manage a device inventory — all
from one unified interface, with an AI chat assistant for natural-language queries.

**Overall style direction:**
- Dark-mode-first enterprise SaaS aesthetic — think Datadog, Grafana, Cisco ThousandEyes,
  or Wiz — technical, dense with data, but clean and never cluttered.
- Primary palette: deep navy blue (#0B2545) and steel blue (#13315C) as base/background,
  teal-green (#1F8A70) as the primary brand accent, and a secondary cyan-blue accent
  (#2E86AB). Use a light neutral grey (#F2F4F7) only for card backgrounds in light mode.
- Status colors: green (#2E9E5B) for healthy/OK, amber (#D98E1E) for warning, red
  (#C1443C) for critical — used consistently across charts, badges, and alerts.
- Typography: clean geometric sans-serif (Inter, Roboto, or IBM Plex Sans style), strong
  hierarchy, tabular numerals for metrics.
- Data-dense but breathable: generous card padding, subtle borders/dividers instead of
  heavy shadows, rounded corners (8–12px), soft glow on critical alerts only.
- Include realistic sample data: server names, IP addresses, CPU/RAM/disk percentages,
  device types (Cisco switch, Linux server, Windows server), timestamps, health scores.
- Left sidebar navigation with icons for: Dashboard, Supervision, Sécurité, NetDevOps,
  Parc informatique, Rapports, Assistant IA, Administration.
- Top bar with global search, notification bell with badge count, user avatar/role
  (Administrateur / Technicien / Visiteur), and a dark/light mode toggle.

Generate the following screens as a cohesive design system sharing the same navigation,
color tokens, and component library.

---

## ÉCRAN 1 — Tableau de bord principal (Dashboard)

A command-center overview screen with:
- Top row of 4–5 KPI cards: total devices monitored, active critical alerts, average
  health score (%), predicted incidents this week, network compliance score (%).
- A large area/line chart showing resource trends (CPU/RAM/disk) across the fleet over
  the last 7 days, with a subtle predicted-trend dashed line extending into the future.
- A device status grid/list showing equipment as colored health chips (green/amber/red)
  with name, IP, type icon, and a mini sparkline per row.
- A live "recent alerts" feed panel (right sidebar or bottom section) with severity
  badges, timestamps, and module origin tags (Sécurité / Supervision / NetDevOps).
- A small donut chart showing device type breakdown (servers, switches, routers).

## ÉCRAN 2 — Module Sécurité (détection d'anomalies)

- A real-time anomaly detection feed: table of security events with source IP, targeted
  user, event type, anomaly score (0–100 with a colored gauge/bar), severity badge, and
  timestamp.
- A scatter plot or timeline visualization showing normal vs anomalous login attempts
  clustered by time, styled like an Isolation Forest output (normal points in muted
  blue, anomalies highlighted in red with a subtle glow).
- Filters for severity, date range, and source IP.
- A detail drawer/modal that opens on click showing full event context and a
  "mark as resolved / escalate" action.

## ÉCRAN 3 — Module Supervision (prédiction de panne)

- Per-device metric detail view: line charts for CPU, RAM, disk, network I/O with a
  clear "prediction zone" (dashed/shaded area) projecting the trend forward.
- A prominent "Time-To-Failure" callout card (e.g., "Saturation disque estimée dans
  4 jours et 6 heures") with a countdown-style visual and severity color.
- A threshold configuration panel (sliders for warning/critical thresholds).
- List of equipment sorted by urgency (soonest predicted failure first).

## ÉCRAN 4 — Module NetDevOps (audit réseau)

- Equipment audit list with a compliance score badge per device (based on CIS
  Benchmark), showing "X findings" with severity breakdown icons.
- An audit detail view: left column lists findings (e.g., "Mot de passe en clair
  détecté", "SNMP v1 non sécurisé actif") each tagged to a CIS rule; right column shows
  a code-diff style preview of the AI-suggested correction (Cisco IOS commands) with
  "Approuver" / "Rejeter" buttons — emphasize human validation before any change.
- A configuration backup history timeline per device with restore action.

## ÉCRAN 5 — Module Gestion de parc (inventaire)

- A searchable/filterable equipment inventory table: name, IP, MAC, OS/firmware,
  uptime, health score (circular progress indicator), last seen.
- A network topology map view (simplified interactive graph) showing devices as nodes
  connected by lines, color-coded by health status.
- An equipment detail page combining data from all modules: metrics history, security
  events, audit history, and backups for that single device.

## ÉCRAN 6 — Assistant IA (chat)

- A clean chat interface docked on the right or as a full page, styled like a technical
  copilot (similar to GitHub Copilot Chat or Linear's AI assistant).
- Example conversation showing a natural-language question ("Quels serveurs risquent une
  saturation disque cette semaine ?") answered with a short text response plus an
  embedded mini data table or chart card inline in the chat.
- Suggested question chips below the input field.
- A small "lecture seule" (read-only) badge/indicator communicating the assistant cannot
  take destructive actions.

## ÉCRAN 7 — Rapports & Administration

- A reports library: list of auto-generated PDF audit/summary reports with date,
  period, and download icon.
- User management table for Administrateur view: username, role badge (Administrateur/
  Technicien/Visiteur), MFA status icon, last login, actions.
- An activity/audit log table with timestamp, user, action, target — dense, monospace-
  leaning for log readability.
- Notification channel settings panel with toggle switches for Email / Telegram /
  Discord and severity-level routing rules.

---

## Notes d'usage
- Génère d'abord l'Écran 1 (Dashboard) pour poser le système de design, puis demande à
  Stitch de "réutiliser ce design system" pour les écrans suivants afin de garder une
  cohérence visuelle totale.
- Si Stitch propose plusieurs variantes, privilégie systématiquement celle en mode
  sombre avec le moins de bruit visuel (cartes bien délimitées, hiérarchie typographique
  claire) — c'est ce registre qui inspire le plus confiance pour un outil d'administration
  système/réseau.
