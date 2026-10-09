#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

BASE_UNIT="cm"
PAPER="letter"
while [[ $# -gt 0 ]]; do
  case "$1" in
    -base)
      if [[ $# -lt 2 ]]; then
        echo "Usage: $0 [-base cm|inches|quarter-inch] [-paper letter|a4]" >&2
        exit 1
      fi
      BASE_UNIT="$2"
      shift 2
      ;;
    -paper)
      if [[ $# -lt 2 ]]; then
        echo "Usage: $0 [-base cm|inches|quarter-inch] [-paper letter|a4]" >&2
        exit 1
      fi
      PAPER="$2"
      shift 2
      ;;
    -h | --help)
      echo "Usage: $0 [-base cm|inches|quarter-inch] [-paper letter|a4]"
      echo "  -base    Grid base unit (default: cm)"
      echo "  -paper   Paper size (default: letter)"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Usage: $0 [-base cm|inches|quarter-inch] [-paper letter|a4]" >&2
      exit 1
      ;;
  esac
done

case "$BASE_UNIT" in
  cm | inches | quarter-inch) ;;
  *)
    echo "Invalid -base value: $BASE_UNIT (use cm, inches, or quarter-inch)" >&2
    exit 1
    ;;
esac

case "$PAPER" in
  letter | a4) ;;
  *)
    echo "Invalid -paper value: $PAPER (use letter or a4)" >&2
    exit 1
    ;;
esac

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck source=/dev/null
source .venv/bin/activate
pip install -q -r requirements.txt

case "$BASE_UNIT" in
  cm) BASE_FILE="cm" ;;
  inches) BASE_FILE="inch" ;;
  quarter-inch) BASE_FILE="quarter-inch" ;;
esac

OUTPUT="$ROOT/output/fractional-grid-${BASE_FILE}-${PAPER}.pdf"
python main.py --base "$BASE_UNIT" --paper "$PAPER"
open "$OUTPUT"
