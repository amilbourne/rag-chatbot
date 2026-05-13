# Frontend Changes

## Code Quality Tooling

### What was added

**Prettier** — the standard zero-config formatter for JavaScript, HTML, and CSS (the frontend equivalent of Black for Python).

| File | Purpose |
|---|---|
| `package.json` | Declares Prettier as a dev dependency; exposes `npm run format` and `npm run format:check` |
| `.prettierrc` | Formatting rules: 2-space indent, single quotes, 100-char line width, LF line endings, trailing commas (ES5) |
| `.prettierignore` | Excludes `node_modules/`, `chroma_db/`, and lockfiles |
| `scripts/format-frontend.sh` | Formats all `frontend/` files in-place |
| `scripts/check-frontend.sh` | CI-style check — exits non-zero if any file is not formatted |

`.gitignore` was updated to exclude `node_modules/`.

### Formatting applied

Prettier was run against all three frontend files. Key changes:

- `index.html` — consistent 2-space nesting, lowercase `<!doctype html>`, self-closing void elements (`<meta />`, `<link />`, `<input />`)
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
