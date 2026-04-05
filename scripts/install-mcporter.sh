#!/bin/bash
# MIT License — Copyright (c) 2026 Victor
# https://github.com/victor0602/minimax-toolkit
#
# MiniMax mcporter 自动安装脚本
# 用法: bash scripts/install-mcporter.sh
#
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置 - 使用环境变量或脚本所在目录的相对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MCPORTER_CONFIG_DIR="${OPENCLAW_CONFIG_DIR:-${PROJECT_ROOT}/config}"
MCPORTER_CONFIG_FILE="${MCPORTER_CONFIG_DIR}/mcporter.json"
MINIMAX_PACKAGE="minimax-coding-plan-mcp"

echo "======================================"
echo "MiniMax mcporter 自动安装脚本"
echo "======================================"
echo ""

# 1. 检测或安装 uvx
echo "[1/5] 检测 uvx (MCP 服务器运行环境)..."
if command -v uvx &> /dev/null || command -v uv &> /dev/null; then
    UV_CMD=$(command -v uvx 2>/dev/null || command -v uv 2>/dev/null)
    echo -e "${GREEN}✓ uvx 已安装: $UV_CMD${NC}"
else
    echo -e "${YELLOW}! uvx 未找到，正在安装 uv...${NC}"
    # Download to temp file first, then execute (avoid pipe-to-shell)
    install_script=$(mktemp)
    # Trap to clean up on exit/interrupt
    trap "rm -f \"$install_script\"" EXIT INT TERM
    curl -LsSf https://astral.sh/uv/install.sh -o "$install_script"
    # Verify non-empty before executing
    if [[ ! -s "$install_script" ]]; then
      echo -e "${RED}✗ Downloaded install script is empty${NC}"
      exit 1
    fi
    bash "$install_script"
    export PATH="$HOME/.local/bin:$PATH"
    if command -v uvx &> /dev/null || command -v uv &> /dev/null; then
        echo -e "${GREEN}✓ uv 安装成功${NC}"
    else
        echo -e "${RED}✗ uv 安装失败，请手动安装: https://astral.sh/uv${NC}"
        exit 1
    fi
fi

# 2. 检测或安装 mcporter
echo ""
echo "[2/5] 检测 mcporter CLI..."
if command -v mcporter &> /dev/null; then
    MCPORTER_VERSION=$(mcporter --version 2>&1 | head -1)
    echo -e "${GREEN}✓ mcporter 已安装: $MCPORTER_VERSION${NC}"
else
    echo -e "${YELLOW}! mcporter 未找到，正在安装...${NC}"
    npm install -g @openwhatsapp/mcporter
    if command -v mcporter &> /dev/null; then
        echo -e "${GREEN}✓ mcporter 安装成功${NC}"
    else
        echo -e "${RED}✗ mcporter 安装失败，请检查 npm 是否可用${NC}"
        exit 1
    fi
fi

# 3. 引导用户输入 API Key
echo ""
echo "[3/5] MiniMax API Key 配置..."
if [ -f "$MCPORTER_CONFIG_FILE" ]; then
    # 从现有配置读取（如果存在且有 MiniMax 配置）
    EXISTING_KEY=$(grep -o '"MINIMAX_API_KEY": "[^"]*"' "$MCPORTER_CONFIG_FILE" 2>/dev/null | head -1 | sed 's/.*: "//;s/"$//')
    if [ -n "$EXISTING_KEY" ]; then
        echo -e "${GREEN}✓ 已找到现有配置，API Key 前缀: ${EXISTING_KEY:0:8}...${NC}"
        echo -n "是否更新 API Key？输入新 Key 直接回车跳过: " >&2
        read -rs NEW_KEY < /dev/tty
        echo >&2
        if [ -n "$NEW_KEY" ]; then
            MINIMAX_API_KEY="$NEW_KEY"
        else
            MINIMAX_API_KEY="$EXISTING_KEY"
        fi
    else
        echo -n "请输入你的 MiniMax Token Plan API Key (sk-cp- 开头): " >&2
        read -rs MINIMAX_API_KEY < /dev/tty
        echo >&2
    fi
else
    echo -n "请输入你的 MiniMax Token Plan API Key (sk-cp- 开头): " >&2
    read -rs MINIMAX_API_KEY < /dev/tty
    echo >&2
fi

if [ -z "$MINIMAX_API_KEY" ]; then
    echo -e "${RED}✗ API Key 不能为空${NC}"
    exit 1
fi

# 4. 创建配置文件
echo ""
echo "[4/5] 创建/更新 mcporter 配置文件..."
mkdir -p "$MCPORTER_CONFIG_DIR"

# 合并现有配置（保留 miot 等其他 server）
if [ -f "$MCPORTER_CONFIG_FILE" ]; then
    echo -e "${GREEN}✓ 发现现有配置，保留其他 MCP 服务器${NC}"
    # 用 python 处理 JSON 合并，更安全（通过环境变量传参，避免特殊字符转义问题）
    MCPORTER_CONFIG_FILE="$MCPORTER_CONFIG_FILE" \
    MINIMAX_API_KEY="$MINIMAX_API_KEY" \
    MINIMAX_PACKAGE="$MINIMAX_PACKAGE" \
    python3 -c "
import json
import os

config_path = os.environ.get('MCPORTER_CONFIG_FILE', '')
if not config_path:
    raise RuntimeError('MCPORTER_CONFIG_FILE not set')
config_path = os.path.expanduser(config_path)
api_key = os.environ.get('MINIMAX_API_KEY', '')
package = os.environ.get('MINIMAX_PACKAGE', '')
if not api_key or not package:
    raise RuntimeError('MINIMAX_API_KEY or MINIMAX_PACKAGE not set')

with open(config_path, 'r') as f:
    config = json.load(f)

if 'mcpServers' not in config:
    config['mcpServers'] = {}

config['mcpServers']['MiniMax'] = {
    'command': 'uvx',
    'args': [package, '-y'],
    'env': {
        'MINIMAX_API_KEY': api_key,
        'MINIMAX_API_HOST': 'https://api.minimaxi.com'
    }
}

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
print('JSON merge done')
"
else
    cat > "$MCPORTER_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "MiniMax": {
      "command": "uvx",
      "args": ["${MINIMAX_PACKAGE}", "-y"],
      "env": {
        "MINIMAX_API_KEY": "${MINIMAX_API_KEY}",
        "MINIMAX_API_HOST": "https://api.minimaxi.com"
      }
    }
  },
  "imports": []
}
EOF
    echo -e "${GREEN}✓ 配置文件已创建${NC}"
fi

# 5. 验证
echo ""
echo "[5/5] 验证配置..."
sleep 1
echo "执行: mcporter list"
echo ""
if mcporter list 2>&1; then
    echo ""
    echo -e "${GREEN}======================================"
    echo -e "✓ 安装成功！MiniMax MCP 已配置完成"
    echo -e "======================================${NC}"
    echo ""
    echo "接下来你可以："
    echo "  - 重新启动 OpenClaw Gateway（使配置生效）"
    echo "  - 使用 'mcporter call MiniMax.web_search' 测试联网搜索"
    echo "  - 使用 'mcporter call MiniMax.understand_image' 测试图片理解"
else
    echo ""
    echo -e "${YELLOW}! mcporter list 验证失败，但配置已保存${NC}"
    echo "请手动执行: mcporter list 查看错误信息"
fi
