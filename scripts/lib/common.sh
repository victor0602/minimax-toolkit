#!/usr/bin/env bash
# MIT License — Copyright (c) 2026 Victor
# https://github.com/victor0602/minimax-toolkit
#
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

# Validate output path to prevent path traversal
# Usage: validate_output_path "$output"
validate_output_path() {
  local output="$1"
  if [[ -z "$output" ]]; then
    return 0
  fi
  # Block path traversal
  if [[ "$output" == *..* ]]; then
    echo "Error: Path traversal not allowed: $output" >&2
    return 1
  fi
  # Allow relative paths; for absolute paths, ensure they're inside cwd or project root
  if [[ "$output" == /* ]]; then
    local canonical canonical_dir
    canonical="$(cd "$(dirname "$output")" && pwd)/$(basename "$output")"
    canonical_dir="$(cd "$(pwd)" && pwd)"
    if [[ "$canonical" != "$canonical_dir"/* ]]; then
      # Not under cwd — allow only if under PROJECT_ROOT
      if [[ "$canonical" != "$PROJECT_ROOT"/* ]]; then
        echo "Error: Absolute path must be inside project directory: $output" >&2
        return 1
      fi
    fi
  fi
  return 0
}

# Validate an input file path to prevent reading sensitive files
# Usage: validate_input_path "$path"
# Returns 0 if safe (relative path, or absolute inside project/cwd), 1 if blocked
validate_input_path() {
  local path="$1"
  if [[ -z "$path" ]]; then
    return 0
  fi
  # Block path traversal
  if [[ "$path" == *..* ]]; then
    echo "Error: Path traversal not allowed: $path" >&2
    return 1
  fi
  # For absolute paths: only allow inside cwd or project root
  if [[ "$path" == /* ]]; then
    local canonical
    canonical="$(cd "$(dirname "$path")" && pwd)/$(basename "$path")"
    local cwd canonical_cwd
    cwd="$(pwd)"; canonical_cwd="$(cd "$cwd" && pwd)"
    if [[ "$canonical" != "$canonical_cwd"/* ]]; then
      if [[ "$canonical" != "$PROJECT_ROOT"/* ]]; then
        echo "Error: Cannot read files outside project directory: $path" >&2
        return 1
      fi
    fi
  fi
  return 0
}
