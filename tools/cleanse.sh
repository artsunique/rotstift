#!/usr/bin/env bash
#
# cleanse.sh - laesst einen deutschen Entwurf von einer FREMDEN Modellfamilie
# gegenlesen. Ein Modell hoert seinen eigenen Akzent nicht.
#
#   tools/cleanse.sh entwurf.md > gereinigt.md
#
# Herkunft des Entwurfs setzen, damit nicht in die eigene Familie geroutet wird:
#   SLOP_AUTOR=claude   (Default) -> ruft codex / gpt
#   SLOP_AUTOR=gpt                -> ruft claude
#   SLOP_AUTOR=gemini             -> ruft irgendeine fremde CLI
#
# Ohne fremde CLI wird der fertige Prompt ausgegeben, zum Einfuegen in den
# anderen Chat. Das ist kein Fehlerfall, sondern der manuelle Weg.

set -euo pipefail

HIER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WURZEL="$(dirname "$HIER")"
PROMPT_DATEI="$WURZEL/prompts/cleanse.txt"
ZEITLIMIT="${SLOP_TIMEOUT:-180}"
AUTOR="${SLOP_AUTOR:-claude}"

if [ $# -lt 1 ]; then
  echo "Aufruf: tools/cleanse.sh <datei>   (oder: cat datei | tools/cleanse.sh -)" >&2
  exit 2
fi

if [ "$1" = "-" ]; then
  ENTWURF="$(cat)"
else
  [ -f "$1" ] || { echo "Datei nicht gefunden: $1" >&2; exit 2; }
  ENTWURF="$(cat "$1")"
fi

[ -f "$PROMPT_DATEI" ] || { echo "Prompt fehlt: $PROMPT_DATEI" >&2; exit 2; }

VOLLER_PROMPT="$(cat "$PROMPT_DATEI")

--- TEXT ---
$ENTWURF
--- ENDE ---"

hat() { command -v "$1" >/dev/null 2>&1; }

# Zielfamilie bestimmen: nie die eigene
case "$AUTOR" in
  claude)  KANDIDATEN=(codex gemini) ;;
  gpt|codex|chatgpt) KANDIDATEN=(claude gemini) ;;
  gemini|google)     KANDIDATEN=(claude codex) ;;
  *)       KANDIDATEN=(codex claude gemini) ;;
esac

for CLI in "${KANDIDATEN[@]}"; do
  if hat "$CLI"; then
    echo "// gegengelesen von: $CLI (Entwurf stammt von: $AUTOR)" >&2
    case "$CLI" in
      claude) timeout "$ZEITLIMIT" claude -p "$VOLLER_PROMPT" ;;
      codex)  timeout "$ZEITLIMIT" codex exec --sandbox read-only "$VOLLER_PROMPT" ;;
      gemini) timeout "$ZEITLIMIT" gemini -p "$VOLLER_PROMPT" ;;
    esac
    exit 0
  fi
done

cat >&2 <<'HINWEIS'

  Keine fremde CLI gefunden.
  Kopiere den folgenden Prompt in ein Chatfenster der ANDEREN Modellfamilie
  und leite das Ergebnis danach wieder durch den Linter.

HINWEIS

printf '%s\n' "$VOLLER_PROMPT"
exit 0
