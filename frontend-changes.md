# Frontend Changes

## Dark / Light Theme Toggle

### Summary

Added a theme toggle button that lets users switch between the existing dark theme and a new light theme. The toggle is a round icon button fixed in the top-right corner of the viewport.

### Files Changed

#### `frontend/index.html`

- Added `data-theme="dark"` to `<html>` to establish dark as the explicit default.
- Added `<button id="themeToggle">` (fixed top-right, `position: fixed`) containing two SVG icons:
  - `.icon-sun` — visible in dark mode; clicking switches to light.
  - `.icon-moon` — visible in light mode; clicking switches to dark.
- Bumped cache-busting versions: `style.css?v=10`, `script.js?v=10`.

#### `frontend/style.css`

- **`[data-theme="light"]` block** — overrides all `:root` CSS variables for the light palette.
- **Smooth transition rule** — added `transition` on key structural elements so theme switches animate rather than snap.
- **`#themeToggle` styles** — 40 × 40 px circular button using `--surface` / `--border-color` variables.
- **Icon visibility rules** — CSS shows/hides `.icon-sun` / `.icon-moon` based on `[data-theme]` attribute on `<html>`.
- **Light-mode link overrides** — `[data-theme="light"] .sources-content a` uses `#1d4ed8` / `#1e40af` for contrast.

#### `frontend/script.js`

- Added `themeToggle` to the DOM element references.
- Wired `click` → `toggleTheme()` in `setupEventListeners()`.
- Added `toggleTheme()` function — reads `data-theme` from `document.documentElement`, flips between `"dark"` and `"light"`.

### Design Decisions

| Decision | Rationale |
|---|---|
| `data-theme` on `<html>` | Matches CSS `[data-theme]` selector at the same specificity as `:root`. |
| CSS variables only | All color changes flow through existing variables. |
| No `localStorage` persistence | Kept minimal per scope — defaults to dark on reload. |
| Transition on structural elements only | Avoids fighting existing `transform`/`opacity` animations. |

---

## Code Quality Tooling

### What was added

**Prettier** — zero-config formatter for JavaScript, HTML, and CSS.

| File | Purpose |
|---|---|
| `package.json` | Declares Prettier as a dev dependency; exposes `npm run format` and `npm run format:check` |
| `.prettierrc` | Formatting rules: 2-space indent, single quotes, 100-char line width, LF line endings, trailing commas (ES5) |
| `.prettierignore` | Excludes `node_modules/`, `chroma_db/`, and lockfiles |
| `scripts/format-frontend.sh` | Formats all `frontend/` files in-place |
| `scripts/check-frontend.sh` | CI-style check — exits non-zero if any file is not formatted |

`.gitignore` was updated to exclude `node_modules/`.

### Formatting applied

Prettier was run against all three frontend files:

- `index.html` — consistent 2-space nesting, lowercase `<!doctype html>`, self-closing void elements
- `script.js` — single quotes, trailing commas on multi-line expressions, consistent spacing
- `style.css` — consistent property ordering whitespace

No logic was changed; only whitespace and quote style were normalised.

### Usage

```bash
# Check formatting (use in CI or pre-commit)
./scripts/check-frontend.sh

# Auto-format all frontend files
./scripts/format-frontend.sh

# Or via npm scripts
npm run format:check
npm run format
```
