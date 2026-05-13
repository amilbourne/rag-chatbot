#!/usr/bin/env bash
# Apply Prettier formatting to all frontend files in-place.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> Formatting frontend files with Prettier..."
npx prettier --write frontend/

echo ""
echo "Frontend formatting complete."
