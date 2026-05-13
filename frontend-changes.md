# Frontend Changes: Dark / Light Theme Toggle

## Summary

Added a theme toggle button that lets users switch between the existing dark theme and a new light theme. The toggle is a round icon button fixed in the top-right corner of the viewport.

---

## Files Changed

### `frontend/index.html`

- Added `data-theme="dark"` to `<html>` to establish dark as the explicit default.
- Added `<button id="themeToggle">` (fixed top-right, `position: fixed`) containing two SVG icons:
  - `.icon-sun` — visible in dark mode; clicking switches to light.
  - `.icon-moon` — visible in light mode; clicking switches to dark.
- Bumped cache-busting versions: `style.css?v=10`, `script.js?v=10`.

### `frontend/style.css`

- **`[data-theme="light"]` block** — overrides all `:root` CSS variables for the light palette:
  - `--background: #f8fafc`, `--surface: #ffffff`, `--surface-hover: #f1f5f9`
  - `--text-primary: #0f172a`, `--text-secondary: #64748b`
  - `--border-color: #e2e8f0`
  - `--focus-ring: rgba(37, 99, 235, 0.15)`
  - `--welcome-bg: #eff6ff`, `--welcome-border: #bfdbfe`
- **Smooth transition rule** — added `transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease` to key structural elements (`body`, `.sidebar`, `.message-content`, `#chatInput`, etc.) so theme switches animate rather than snap.
- **`#themeToggle` styles** — 40 × 40 px circular button, uses `--surface` / `--border-color` variables so it inherits theme changes automatically. Hover state highlights with `--primary-color` border.
- **Icon visibility rules** — CSS shows/hides `.icon-sun` / `.icon-moon` based on `[data-theme]` attribute on `<html>`, no JS class toggling needed.
- **Light-mode link overrides** — `[data-theme="light"] .sources-content a` uses `#1d4ed8` / `#1e40af` for proper contrast against the light background.

### `frontend/script.js`

- Added `themeToggle` to the DOM element references.
- Wired `click` → `toggleTheme()` in `setupEventListeners()`.
- Added `toggleTheme()` function — reads `data-theme` from `document.documentElement`, flips it between `"dark"` and `"light"`.

---

## Design Decisions

| Decision | Rationale |
|---|---|
| `data-theme` on `<html>` | Matches CSS `[data-theme]` selector which sits at the same specificity level as `:root`, cleanly overriding variables. |
| CSS variables only | All color changes flow through existing variables; no element-level colour overrides needed (except the hardcoded source link `#60a5fa`). |
| No `localStorage` persistence | Kept minimal per scope — the page defaults to dark on reload. Persistence can be added later without touching the existing logic. |
| Transition on structural elements only | Avoids fighting the existing `transform`/`opacity` animations (fade-in, loading bounce, button hover lift). |
