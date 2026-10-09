#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck source=/dev/null
source .venv/bin/activate
pip install -q -r requirements.txt

mkdir -p "$ROOT/output"

for BASE_UNIT in cm inches quarter-inch; do
  for PAPER in letter a4; do
    python main.py --base "$BASE_UNIT" --paper "$PAPER"
  done
done

echo "All PDFs written to $ROOT/output/"
