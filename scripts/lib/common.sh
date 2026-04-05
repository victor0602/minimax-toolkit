#!/usr/bin/env bash
# Common functions shared by all MiniMax generation scripts
# Source this file: source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

load_env() {
  local env_file
  for env_file in "$PROJECT_ROOT/.env" "$(pwd)/.env"; do
    if [[ -f "$env_file" ]]; then
      while IFS= read -r line || [[ -n "$line" ]]; do
        line="${line%%#*}"; line="$(echo "$line" | xargs)"
        [[ -z "$line" || "$line" != *=* ]] && continue
        local key="${line%%=*}" val="${line#*=}"
        key="$(echo "$key" | xargs)"; val="$(echo "$val" | xargs)"
        if [[ ${#val} -ge 2 ]]; then
          case "$val" in \"*\") val="${val:1:${#val}-2}" ;; \'*\') val="${val:1:${#val}-2}" ;; esac
        fi
        [[ -z "${!key:-}" ]] && export "$key=$val"
      done < "$env_file"
      return 0
    fi
  done
}

check_api_key() {
  if [[ -z "${MINIMAX_API_KEY:-}" ]]; then
    echo "Error: MINIMAX_API_KEY environment variable is not set." >&2; exit 1
  fi
}

# Structured error exit — outputs JSON error and exits
# Usage: error_exit <code> <message> [hint]
error_exit() {
  local code="$1" message="$2" hint="${3:-}"
  local file="${BASH_SOURCE[1]:-unknown}:${BASH_LINENO[0]:-0}"
  local json="{\"error\":{\"code\":\"$code\",\"message\":$(printf '%s' "$message" | jq -Rs .)},\"file\":\"$file\"}"
  if [[ -n "$hint" ]]; then
    json=$(echo "$json" | jq --arg h "$hint" '.error.hint = $h')
  fi
  echo "$json" >&2
  exit 1
}
