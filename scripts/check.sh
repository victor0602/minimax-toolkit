#!/usr/bin/env bash
#
# MiniMax Toolkit diagnostic tool
# Usage: bash scripts/check.sh [--json] [--feature <name>]
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=lib/diagnose.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib/diagnose.sh"

show_usage() {
  cat <<'USAGE'
MiniMax Toolkit Diagnostic Tool

Usage:
  bash scripts/check.sh [options]

Options:
  --json           Output machine-readable JSON lines (one per line)
  --feature <name> Check only a specific feature (tts, image, music, video, mcporter, env)
  -h, --help       Show this help

Examples:
  # Full diagnostic with human-readable output
  bash scripts/check.sh

  # Machine-readable output (for agents)
  bash scripts/check.sh --json

  # Check specific feature
  bash scripts/check.sh --feature tts --json
USAGE
}

run_human() {
  echo "======================================"
  echo "MiniMax Toolkit — Diagnostic Check"
  echo "======================================"
  echo ""

  local start_time end_time elapsed
  start_time=$(date +%s)

  local check_output
  check_output=$(diag_run_all 2>&1) || true
  echo "$check_output" >&2

  echo ""
  end_time=$(date +%s)
  elapsed=$((end_time - start_time))

  echo "======================================"
  echo "Summary (completed in ${elapsed}s)"
  echo "======================================"
  echo ""
  echo "Run with --json flag for machine-readable output."
  echo "For guided setup, run: python3 scripts/toolkit.py setup"
}

run_json() {
  if [[ -n "$feature" ]]; then
    case "$feature" in
      env) diag_check_env ;;
      api_key) diag_check_api_key ;;
      tts) diag_check_tts ;;
      image) diag_check_image ;;
      music) diag_check_music ;;
      video) diag_check_video ;;
      mcporter) diag_check_mcporter ;;
      dependencies) diag_check_dependencies ;;
      *) echo "{\"error\":\"Unknown feature: $feature\"}" >&2; exit 1 ;;
    esac
  else
    diag_run_all
  fi
}

json_output=false
feature=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json) json_output=true; shift ;;
    --feature) feature="$2"; shift 2 ;;
    -h|--help) show_usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; show_usage >&2; exit 1 ;;
  esac
done

if $json_output; then
  run_json
else
  run_human
fi
