#!/usr/bin/env bash
# MIT License — Copyright (c) 2026 Victor
# https://github.com/victor0602/minimax-toolkit
#
# Diagnostic functions for MiniMax Toolkit
# Source this file: source "$(dirname "${BASH_SOURCE[0]}")/../lib/diagnose.sh"
# All functions output structured JSON to stdout and human-readable to stderr.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# shellcheck source=lib/common.sh
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

# ---------------------------------------------------------------------------
# Time helpers (portable millisecond timestamp)
# ---------------------------------------------------------------------------

_date_ms() {
  local out
  # Try Linux format first (works on Linux, fails on macOS)
  out=$(date +%s%3N 2>/dev/null)
  if [[ "$out" =~ ^[0-9]+$ ]]; then
    echo "$out"
    return
  fi
  # Fallback: macOS or other BSD (strip trailing N if present)
  out=$(date +%s000 2>/dev/null) && echo "$out" && return
  # Last resort: python3
  python3 -c 'import time; print(int(time.time()*1000))'
}

# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

_diag_json_escape() {
  printf '%s' "$1" | jq -Rs .
}

# Print a JSON status line to stdout (machine-readable)
# Usage: _json_status <feature> <status> [extra_key_value_pairs...]
_json_status() {
  local feature="$1" status="$2"
  shift 2
  local kv_pairs=("$@")
  local obj="{\"feature\":$(_diag_json_escape "$feature"),\"status\":$(_diag_json_escape "$status")"
  if [[ ${#kv_pairs[@]} -gt 0 ]]; then
    for ((i=0; i<${#kv_pairs[@]}; i+=2)); do
      local key="${kv_pairs[$i]}" val="${kv_pairs[$((i+1))]}"
      obj+=",\"$key\":$(printf '%s' "$val" | jq -Rs .)"
    done
  fi
  obj+="}"
  echo "$obj"
}

# Print human-readable progress to stderr
_diag_echo() {
  echo "[diagnose] $*" >&2
}

# ---------------------------------------------------------------------------
# Dependency checks
# ---------------------------------------------------------------------------

diag_check_dependencies() {
  local deps=("jq" "curl" "ffmpeg" "python3" "base64" "bc")
  local missing=()
  for dep in "${deps[@]}"; do
    if ! command -v "$dep" &>/dev/null; then
      missing+=("$dep")
    fi
  done
  if [[ ${#missing[@]} -gt 0 ]]; then
    _json_status "dependencies" "warn" "missing" "$(IFS=,; echo "${missing[*]}")"
  else
    _json_status "dependencies" "ok"
  fi
}

# Check if a command exists and return its version
diag_check_tool() {
  local name="$1" cmd="$2"
  if command -v "$cmd" &>/dev/null; then
    local ver
    ver="$("$cmd" --version 2>&1 | head -1 || echo "unknown")"
    _json_status "$name" "ok" "version" "$ver"
    return 0
  else
    _json_status "$name" "missing"
    return 1
  fi
}

# ---------------------------------------------------------------------------
# Environment checks
# ---------------------------------------------------------------------------

# Check .env file exists and parse key info
diag_check_env() {
  load_env
  local env_file=""
  for ef in "$PROJECT_ROOT/.env" "$(pwd)/.env"; do
    if [[ -f "$ef" ]]; then
      env_file="$ef"
      break
    fi
  done

  if [[ -z "$env_file" ]]; then
    _json_status "env" "missing" "message" "No .env file found"
    return 1
  fi

  local key_type="unknown"
  local key_prefix=""
  if [[ -n "${MINIMAX_API_KEY:-}" ]]; then
    key_prefix="${MINIMAX_API_KEY:0:6}"
  fi
  case "$key_prefix" in
    sk-cp-*) key_type="token_plan" ;;
    sk-api*) key_type="api_key" ;;
  esac

  # Mask key for display
  local masked_key="${MINIMAX_API_KEY:0:8}..."
  _json_status "env" "ok" \
    "env_file" "$env_file" \
    "api_key_masked" "$masked_key" \
    "api_key_type" "$key_type" \
    "api_host" "${MINIMAX_API_HOST:-https://api.minimaxi.com}"
  return 0
}

# Check if API key is set (shortcut)
diag_check_api_key() {
  load_env
  if [[ -z "${MINIMAX_API_KEY:-}" ]]; then
    _json_status "api_key" "missing"
    return 1
  fi
  local key_type="unknown"
  case "${MINIMAX_API_KEY:0:6}" in
    sk-cp-*) key_type="token_plan" ;;
    sk-api*) key_type="api_key" ;;
  esac
  _json_status "api_key" "ok" "type" "$key_type"
  return 0
}

# ---------------------------------------------------------------------------
# Feature checks — these make real API calls with minimal payloads
# ---------------------------------------------------------------------------

_api_request() {
  local method="$1" endpoint="$2" body="${3:-}"
  local url="${MINIMAX_API_HOST:-https://api.minimaxi.com}/v1/${endpoint#/}"
  local output http_code response
  output="$(curl -s -w "\n%{http_code}" \
    -X "$method" \
    -H "Authorization: Bearer ${MINIMAX_API_KEY}" \
    -H "Content-Type: application/json" \
    -H "Accept-Encoding: gzip, deflate" \
    --compressed \
    --max-time 30 \
    ${body:+-d "$body"} \
    "$url" 2>/dev/null)" || return 1
  http_code="${output##*$'\n'}"
  response="${output%$'\n'*}"
  echo "$response"
  if [[ "$http_code" -ge 400 ]]; then
    return 1
  fi
  return 0
}

# TTS — synthesize a very short text
diag_check_tts() {
  load_env
  if [[ -z "${MINIMAX_API_KEY:-}" ]]; then
    _json_status "tts" "skip" "reason" "No API key"
    return 0
  fi

  local start end latency
  start=$(_date_ms)
  local resp
  resp=$(_api_request POST "t2a_v2" '{"model":"speech-2.8-hd","text":"test","voice_setting":{"voice_id":"female-shaonv","speed":1.0,"vol":1.0,"pitch":0},"audio_setting":{"sample_rate":32000,"bitrate":128000,"format":"mp3","channel":1},"stream":false,"output_format":"hex"}' 2>/dev/null) || {
    local err_msg
    err_msg=$(echo "$resp" | jq -r '.base_resp.status_msg // "request failed"' 2>/dev/null || echo "request failed")
    _json_status "tts" "error" "reason" "$err_msg"
    return 0
  }
  end=$(_date_ms)
  latency=$((end - start))

  local audio_data
  audio_data=$(echo "$resp" | jq -r '.data.audio // .extra_info.audio // empty' 2>/dev/null)
  if [[ -n "$audio_data" && "$audio_data" != "null" ]]; then
    _json_status "tts" "ok" "latency_ms" "$latency"
  else
    _json_status "tts" "error" "reason" "No audio in response"
  fi
}

# Image generation — tiny 1x1 image
diag_check_image() {
  load_env
  if [[ -z "${MINIMAX_API_KEY:-}" ]]; then
    _json_status "image" "skip" "reason" "No API key"
    return 0
  fi

  local start end latency
  start=$(_date_ms)
  local resp
  resp=$(_api_request POST "image_generation" '{"model":"image-01","prompt":"test","response_format":"url","n":1}' 2>/dev/null) || {
    local err_msg
    err_msg=$(echo "$resp" | jq -r '.base_resp.status_msg // "request failed"' 2>/dev/null || echo "request failed")
    _json_status "image" "error" "reason" "$err_msg"
    return 0
  }
  end=$(_date_ms)
  latency=$((end - start))

  local url
  url=$(echo "$resp" | jq -r '.data.image_urls[0] // empty' 2>/dev/null)
  if [[ -n "$url" && "$url" != "null" ]]; then
    _json_status "image" "ok" "latency_ms" "$latency" "url" "$url"
  else
    _json_status "image" "error" "reason" "No image URL in response"
  fi
}

# Music — instrumental short clip
diag_check_music() {
  load_env
  if [[ -z "${MINIMAX_API_KEY:-}" ]]; then
    _json_status "music" "skip" "reason" "No API key"
    return 0
  fi

  local start end latency
  start=$(_date_ms)
  local resp
  resp=$(_api_request POST "music_generation" '{"model":"music-2.5","prompt":"short test","output_format":"url","stream":false}' 2>/dev/null) || {
    local err_msg
    err_msg=$(echo "$resp" | jq -r '.base_resp.status_msg // "request failed"' 2>/dev/null || echo "request failed")
    _json_status "music" "error" "reason" "$err_msg"
    return 0
  }
  end=$(_date_ms)
  latency=$((end - start))

  local audio_url
  audio_url=$(echo "$resp" | jq -r '.data.audio_url // .data.audio // empty' 2>/dev/null)
  if [[ -n "$audio_url" && "$audio_url" != "null" ]]; then
    _json_status "music" "ok" "latency_ms" "$latency" "url" "$audio_url"
  else
    _json_status "music" "error" "reason" "No audio URL in response"
  fi
}

# Video — shortest possible (6s)
diag_check_video() {
  load_env
  if [[ -z "${MINIMAX_API_KEY:-}" ]]; then
    _json_status "video" "skip" "reason" "No API key"
    return 0
  fi

  local start end latency
  start=$(_date_ms)
  local resp
  # Use a simple t2v with minimal prompt
  resp=$(_api_request POST "video_generation" '{"model":"MiniMax-Hailuo-2.3","prompt":"test","duration":6,"resolution":"768P"}' 2>/dev/null) || {
    local err_msg
    err_msg=$(echo "$resp" | jq -r '.base_resp.status_msg // "request failed"' 2>/dev/null || echo "request failed")
    _json_status "video" "error" "reason" "$err_msg"
    return 0
  }
  end=$(_date_ms)
  latency=$((end - start))

  local task_id
  task_id=$(echo "$resp" | jq -r '.task_id // empty' 2>/dev/null)
  if [[ -n "$task_id" && "$task_id" != "null" ]]; then
    _json_status "video" "ok" "latency_ms" "$latency" "task_id" "$task_id"
  else
    _json_status "video" "error" "reason" "No task_id in response"
  fi
}

# mcporter — check CLI and MCP server status
diag_check_mcporter() {
  local cfg_file="${OPENCLAW_CONFIG_DIR:-${PROJECT_ROOT}/config}/mcporter.json"

  if ! command -v mcporter &>/dev/null; then
    _json_status "mcporter" "missing" "reason" "mcporter CLI not installed"
    return 0
  fi

  local cli_version
  cli_version=$(mcporter --version 2>&1 | head -1 || echo "unknown")
  _json_status "mcporter" "ok" "cli_version" "$cli_version" "config_file" "$cfg_file"

  # Check config
  if [[ -f "$cfg_file" ]]; then
    local has_minimax
    has_minimax=$(jq -r '.mcpServers.MiniMax // empty' "$cfg_file" 2>/dev/null)
    if [[ -n "$has_minimax" && "$has_minimax" != "null" ]]; then
      _diag_echo "mcporter MiniMax config: found"
    else
      _diag_echo "mcporter MiniMax config: not configured"
    fi
  fi

  # Try to list servers
  local list_output
  if list_output=$(mcporter list 2>&1); then
    local servers
    servers=$(echo "$list_output" | grep -v "^$" | head -5 | jq -R . | jq -s . 2>/dev/null || echo "[]")
    _json_status "mcporter" "ok" "servers" "$servers"
  else
    _json_status "mcporter" "warn" "reason" "mcporter list failed" "detail" "$(echo "$list_output" | head -3 | jq -Rs .)"
  fi
}

# ---------------------------------------------------------------------------
# Run all checks — outputs newline-delimited JSON lines to stdout
# ---------------------------------------------------------------------------

diag_run_all() {
  _diag_echo "Checking environment..."
  diag_check_env || true

  _diag_echo "Checking dependencies..."
  diag_check_dependencies || true

  _diag_echo "Checking API key..."
  diag_check_api_key || true

  _diag_echo "Checking TTS..."
  diag_check_tts || true

  _diag_echo "Checking image generation..."
  diag_check_image || true

  _diag_echo "Checking music generation..."
  diag_check_music || true

  _diag_echo "Checking video generation..."
  diag_check_video || true

  _diag_echo "Checking mcporter..."
  diag_check_mcporter || true
}
