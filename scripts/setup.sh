#!/usr/bin/env bash
#
# MiniMax Toolkit first-run setup wizard
# Usage: bash scripts/setup.sh [--non-interactive]
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()    { echo -e "${CYAN}[INFO]${NC}  $*" >&2; }
success() { echo -e "${GREEN}[OK]${NC}   $*" >&2; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
error()   { echo -e "${RED}[ERR]${NC}  $*" >&2; }

# shellcheck source=lib/diagnose.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib/diagnose.sh"

show_banner() {
  echo ""
  echo "============================================"
  echo "  MiniMax Toolkit — Setup Wizard"
  echo "============================================"
  echo ""
}

# Check if running interactively
is_tty() {
  [[ -t 0 ]]
}

# Prompt for input (reads from stdin / dev/tty)
prompt_input() {
  local prompt="$1" var_name="$2"
  if is_tty; then
    echo -n "$prompt: " >&2
    read -r "$var_name" < /dev/tty
  else
    error "Interactive input required but no TTY available. Use --non-interactive with env vars."
    exit 1
  fi
}

# Check dependencies
check_deps() {
  info "Checking dependencies..."
  local missing=()
  for dep in jq curl ffmpeg python3; do
    if ! command -v "$dep" &>/dev/null; then
      missing+=("$dep")
    fi
  done
  if [[ ${#missing[@]} -gt 0 ]]; then
    error "Missing required tools: ${missing[*]}"
    info "Install with: brew install ${missing[*]}"
    return 1
  fi
  local jq_ver ffmpeg_ver
  jq_ver=$(jq --version 2>&1)
  ffmpeg_ver=$(ffmpeg -version 2>&1 | head -1)
  success "Dependencies OK (jq $jq_ver, ffmpeg $(echo "$ffmpeg_ver" | awk '{print $3}'))"
  return 0
}

# Check / setup .env
check_env_file() {
  local env_file="$PROJECT_ROOT/.env"
  if [[ -f "$env_file" ]]; then
    # Load it to check format
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

    if [[ -z "${MINIMAX_API_KEY:-}" ]]; then
      warn ".env file exists but MINIMAX_API_KEY is empty."
      return 2
    fi
    success ".env found with API key: ${MINIMAX_API_KEY:0:8}..."
    return 0
  else
    info ".env file not found. Will create from template."
    return 1
  fi
}

# Setup .env
setup_env_file() {
  local api_key="${MINIMAX_API_KEY:-}"
  local feishu_app_id="${FEISHU_APP_ID:-}"
  local feishu_app_secret="${FEISHU_APP_SECRET:-}"

  # Check if we have existing env vars to use
  if [[ -n "$api_key" && "$api_key" != "sk-cp-xxx" && "$api_key" != "sk-api-xxx" && "$api_key" != "YOUR_API_KEY" ]]; then
    info "Found MINIMAX_API_KEY in environment: ${api_key:0:8}..."
    if is_tty; then
      echo -n "Use this API key? [Y/n]: " >&2
      read -r use_existing < /dev/tty
      use_existing="${use_existing:-Y}"
      if [[ "$use_existing" =~ ^[Nn]$ ]]; then
        api_key=""
      fi
    fi
  fi

  if [[ -z "$api_key" ]]; then
    prompt_input "Enter your MiniMax API Key (sk-cp- or sk-api-)" api_key
    api_key=$(echo "$api_key" | xargs)
  fi

  if [[ -z "$api_key" ]]; then
    error "API Key cannot be empty."
    exit 1
  fi

  if [[ "$api_key" != sk-cp-* && "$api_key" != sk-api-* ]]; then
    warn "API Key should start with 'sk-cp-' or 'sk-api-'. Proceeding anyway..."
  fi

  # Check for Feishu env vars
  if [[ -n "$feishu_app_id" && -n "$feishu_app_secret" ]]; then
    info "Found Feishu credentials in environment"
    if is_tty; then
      echo -n "Use this Feishu configuration? [Y/n]: " >&2
      read -r use_existing_feishu < /dev/tty
      use_existing_feishu="${use_existing_feishu:-Y}"
      if [[ "$use_existing_feishu" =~ ^[Nn]$ ]]; then
        feishu_app_id=""
        feishu_app_secret=""
      fi
    fi
  fi

  if [[ -z "$feishu_app_id" ]]; then
    if is_tty; then
      echo -n "Enter Feishu App ID (leave empty to skip): " >&2
      read -r feishu_app_id < /dev/tty
      feishu_app_id=$(echo "$feishu_app_id" | xargs)
    fi
  fi

  if [[ -z "$feishu_app_secret" && -n "$feishu_app_id" ]]; then
    if is_tty; then
      echo -n "Enter Feishu App Secret: " >&2
      read -r feishu_app_secret < /dev/tty
      feishu_app_secret=$(echo "$feishu_app_secret" | xargs)
    fi
  fi

  local env_file="$PROJECT_ROOT/.env"
  cat > "$env_file" <<EOF
# MiniMax API 配置
# 复制此文件为 .env 并填入你的真实密钥

# API Key（sk-cp- 开头为 Token Plan Key，sk-api- 开头为 API Key）
MINIMAX_API_KEY=$api_key

# API 地址（默认中国大陆）
MINIMAX_API_HOST=https://api.minimaxi.com

# Feishu 配置（可选）
FEISHU_APP_ID=${feishu_app_id:-}
FEISHU_APP_SECRET=${feishu_app_secret:-}
EOF

  success ".env file created at $env_file"
  # Load it
  export MINIMAX_API_KEY="$api_key"
  export MINIMAX_API_HOST="https://api.minimaxi.com"
  [[ -n "$feishu_app_id" ]] && export FEISHU_APP_ID="$feishu_app_id"
  [[ -n "$feishu_app_secret" ]] && export FEISHU_APP_SECRET="$feishu_app_secret"
}

# Validate API key via list-voices
validate_api_key() {
  info "Validating API key..."
  local resp http_code
  resp="$(curl -s -w "\n%{http_code}" \
    -X POST "${MINIMAX_API_HOST:-https://api.minimaxi.com}/v1/voice/list" \
    -H "Authorization: Bearer ${MINIMAX_API_KEY}" \
    -H "Content-Type: application/json" \
    -d '{"voice_type":"system"}' \
    --max-time 15 \
    2>/dev/null)" || true

  http_code="${resp##*$'\n'}"
  local body="${resp%$'\n'*}"

  if [[ "$http_code" -ge 400 ]]; then
    local err_msg
    err_msg=$(echo "$body" | jq -r '.base_resp.status_msg // "HTTP error"' 2>/dev/null || echo "HTTP $http_code")
    error "API Key validation failed: $err_msg"
    info "Hint: Make sure you have a valid Token Plan Key (sk-cp-...) for TTS/Music/Video features."
    return 1
  fi

  local key_type="unknown"
  case "${MINIMAX_API_KEY:0:5}" in
    sk-cp-) key_type="Token Plan (sk-cp-)" ;;
    sk-api) key_type="API Key (sk-api-)" ;;
  esac
  success "API Key valid ($key_type)"
  return 0
}

# Install mcporter
setup_mcporter() {
  info "Checking mcporter..."
  if command -v mcporter &>/dev/null; then
    local ver
    ver=$(mcporter --version 2>&1 | head -1)
    success "mcporter already installed: $ver"
    return 0
  fi

  warn "mcporter not found. Running installer..."
  if [[ ! is_tty ]]; then
    warn "Interactive install requires TTY. Run interactively to install mcporter."
    return 0
  fi

  bash "$SCRIPT_DIR/install-mcporter.sh"
}

# Run feature checks
run_feature_checks() {
  info "Running feature checks..."
  echo ""

  local results=()

  check_result "TTS" diag_check_tts
  check_result "Image Generation" diag_check_image
  check_result "Music Generation" diag_check_music
  check_result "Video Generation" diag_check_video
  check_result "mcporter" diag_check_mcporter

  echo ""
  info "Feature check complete."
}

check_result() {
  local label="$1" check_func="$2"
  printf "  %-20s " "$label:" >&2

  local output exit_code=0
  output=$("$check_func" 2>&1) || exit_code=$?

  local status
  status=$(echo "$output" | jq -r '.status' 2>/dev/null || echo "error")

  case "$status" in
    ok)     echo -e "${GREEN}✓ OK${NC}" >&2; return 0 ;;
    warn)   echo -e "${YELLOW}⚠ WARN${NC}" >&2; return 0 ;;
    skip)   echo -e "${YELLOW}⊘ SKIP${NC}" >&2; return 0 ;;
    missing) echo -e "${RED}✗ MISSING${NC}" >&2; return 0 ;;
    error)  echo -e "${RED}✗ ERROR${NC}" >&2; return 0 ;;
    *)      echo -e "${RED}✗ UNKNOWN${NC}" >&2; return 1 ;;
  esac
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

main() {
  local non_interactive=false
  if [[ "${1:-}" == "--non-interactive" ]]; then
    non_interactive=true
  fi

  show_banner

  # 1. Dependencies
  info "Step 1/4 — Checking dependencies..."
  if ! check_deps; then
    error "Please install missing dependencies and re-run setup."
    exit 1
  fi

  echo ""

  # 2. Env file
  info "Step 2/4 — Environment configuration..."
  local env_status
  check_env_file || env_status=$?
  case "${env_status:-0}" in
    0) ;;
    2) warn "API key empty — please update $PROJECT_ROOT/.env";;
    1)
      if $non_interactive && [[ -z "${MINIMAX_API_KEY:-}" ]]; then
        error "No .env and no MINIMAX_API_KEY env var. Provide API key to continue."
        exit 1
      fi
      setup_env_file || exit 1
      ;;
  esac

  echo ""

  # 3. API key validation
  info "Step 3/4 — Validating API key..."
  if [[ -z "${MINIMAX_API_KEY:-}" ]]; then
    warn "MINIMAX_API_KEY not set. Set it in .env or environment and re-run."
  else
    validate_api_key || {
      warn "API key validation failed. Setup will continue but some features may not work."
    }
  fi

  echo ""

  # 4. Feature checks
  info "Step 4/4 — Feature checks..."
  run_feature_checks

  echo ""
  echo "============================================"
  success "Setup complete!"
  echo "============================================"
  echo ""
  echo "Next steps:"
  echo "  python3 scripts/toolkit.py check --json   # Verify everything (for agents)"
  echo "  python3 scripts/toolkit.py tts \"hello\"   # Try TTS"
  echo ""
  echo "For mcporter (image understanding + web search), run:"
  echo "  bash scripts/install-mcporter.sh"
  echo ""
}

main "$@"
