#!/usr/bin/env bash
# Run frontend code quality checks.
# Exit code 0 = all checks passed, non-zero = failures found.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> Checking frontend formatting with Prettier..."
npx prettier --check frontend/

echo ""
echo "All frontend checks passed."
