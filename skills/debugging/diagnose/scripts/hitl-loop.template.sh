#!/usr/bin/env bash
# hitl-loop.template.sh — structured human-in-the-loop feedback loop.
#
# Last-resort feedback loop for Phase 1 of the diagnose skill: use it only when
# a step genuinely requires a human (a manual click, a physical action, a
# credential the agent can't hold). It keeps the loop disciplined even with a
# human in it — one action per iteration, captured output, a clear pass/fail
# signal that feeds back to the agent.
#
# This is a TEMPLATE. Copy it next to your repro, fill in the three blanks
# marked TODO, and run it. Each iteration is logged to a timestamped file so
# every run is a breadcrumb (see the mantra).
#
# Usage:
#   cp hitl-loop.template.sh /tmp/hitl-loop.sh
#   $EDITOR /tmp/hitl-loop.sh   # fill in the TODOs
#   bash /tmp/hitl-loop.sh

set -uo pipefail

# ── TODO 1: what the human must do each iteration ─────────────────────────────
ACTION_INSTRUCTIONS=$(cat <<'EOF'
TODO: describe the exact action the human should perform, e.g.
  1. Open https://app.example.com/checkout in a fresh incognito window
  2. Add SKU-123 to the cart and click "Pay"
  3. Note the exact error banner text and the request id from the network tab
EOF
)

# ── TODO 2: the symptom that means "still failing" ────────────────────────────
SYMPTOM="TODO: the failure you're hunting, e.g. 'HTTP 500 on POST /pay'"

LOG_DIR="${HITL_LOG_DIR:-./hitl-runs}"
mkdir -p "$LOG_DIR"
run=0

echo "=== HITL diagnosis loop — symptom: $SYMPTOM ==="
echo "Logs: $LOG_DIR/  (Ctrl-C to stop)"
echo

while true; do
  run=$((run + 1))
  ts=$(date +%Y%m%d-%H%M%S)
  log="$LOG_DIR/run-$run-$ts.log"

  echo "────────── iteration $run ──────────"
  echo "$ACTION_INSTRUCTIONS"
  echo

  # ── TODO 3 (optional): automate any setup you CAN before the human acts ─────
  # e.g. reset state, tail a log, start a capture. Output is appended to $log.
  : # no-op by default

  printf 'Paste the observed result (end with an empty line):\n'
  observed=""
  while IFS= read -r line; do
    [ -z "$line" ] && break
    observed+="$line"$'\n'
  done

  {
    echo "iteration: $run"
    echo "timestamp: $ts"
    echo "symptom:   $SYMPTOM"
    echo "--- observed ---"
    echo "$observed"
  } > "$log"
  echo "  saved -> $log"

  printf 'Did the symptom appear this run? [y]es / [n]o / [q]uit: '
  read -r verdict
  case "$verdict" in
    y|Y) echo "  -> REPRODUCED. Feed $log back to the agent as the latest breadcrumb." ;;
    n|N) echo "  -> not reproduced this run (still a breadcrumb — note what differed)." ;;
    q|Q) echo "Stopping. ${run} run(s) captured in $LOG_DIR/."; exit 0 ;;
    *)   echo "  -> unrecognised; logged as inconclusive." ;;
  esac
  echo
done
