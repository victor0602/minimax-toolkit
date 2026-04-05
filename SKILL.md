---
name: minimax-toolkit
description: MiniMax 全功能工具包。触发词：minimax、生成图片、生成语音、生成音乐、生成视频、配置 minimax。Agent 首先运行 `python3 scripts/toolkit.py check --json` 了解环境状态。
---

# MiniMax 全功能工具包

## Agent 快速入门

**第一步（必做）**：了解当前环境状态：
```bash
python3 scripts/toolkit.py check --json
```

这会返回结构化 JSON，告诉你：
- API Key 是否配置、类型是否正确
- 每个功能（TTS/图片/音乐/视频/mcporter）的可用状态
- 依赖工具是否完整
- 具体问题所在及修复建议

**第二步**：根据状态调用对应功能：
```bash
python3 scripts/toolkit.py setup          # 首次使用引导配置
python3 scripts/toolkit.py env --show      # 查看当前配置
python3 scripts/toolkit.py env --key xxx   # 设置 API Key
python3 scripts/toolkit.py tts "你好"      # 语音合成
python3 scripts/toolkit.py image "一只猫"  # 图片生成
python3 scripts/toolkit.py music --prompt "轻快流行" # 音乐生成
python3 scripts/toolkit.py video --prompt "猫在屋顶"  # 视频生成
```

---

## 统一入口

```
python3 scripts/toolkit.py <command> [options]
```

| 命令 | 说明 |
|------|------|
| `check [--json]` | 检查所有功能状态，JSON 供 agent 解析 |
| `setup` | 首次运行引导，完成全部配置 |
| `env --show` | 显示当前环境变量 |
| `env --key <key>` | 设置 API Key |
| `tts <text> [-v voice] [-o file]` | 语音合成 |
| `image <prompt> [-o file]` | 图片生成 |
| `music --prompt <style> [--lyrics "歌词"]` | 音乐生成 |
| `video --prompt <desc> [--mode t2v] [-o file]` | 视频生成 |
| `feishu list` | 列出机器人所在的所有群聊 |
| `feishu send <file>` | 发送文件到选定的群聊（交互式选择） |

---

## 环境配置

| 变量 | 说明 | 示例 |
|------|------|------|
| `MINIMAX_API_KEY` | MiniMax API Key | `sk-cp-xxxxx` 或 `sk-api-xxxxx` |
| `MINIMAX_API_HOST` | API 地址（默认中国大陆） | `https://api.minimaxi.com` |
| `FEISHU_APP_ID` | 飞书机器人 App ID | `cli_xxxxx` |
| `FEISHU_APP_SECRET` | 飞书机器人 App Secret | `xxxxx` |
| `FEISHU_CHAT_ID` | 默认推送群 ID | `oc_xxxxx` |

**API Key 类型说明：**
- `sk-cp-` 开头 = **Token Plan Key**（推荐），支持 TTS/音乐/视频/图片
- `sk-api-` 开头 = API Key，支持部分功能

**mcporter 配置**（图片理解 + 联网搜索）有独立全局配置，通过 `install-mcporter.sh` 管理。

---

## 错误码（供 Agent 解析）

所有功能调用失败时返回结构化 JSON 错误：

```json
{"error":{"code":"E_API_KEY_MISSING","message":"MINIMAX_API_KEY is not set","hint":"Run: python3 scripts/toolkit.py env --key <your-api-key>","file":"scripts/toolkit.py:41"}}
```

| 错误码 | 含义 | 解决方法 |
|--------|------|---------|
| `E_API_KEY_MISSING` | 未设置 API Key | `toolkit.py env --key <key>` |
| `E_API_KEY_INVALID` | API Key 无效或权限不足 | 检查 Key 类型（sk-cp- vs sk-api-） |
| `E_API_NETWORK` | 网络错误 | 检查网络/代理设置 |
| `E_API_TIMEOUT` | API 超时 | 重试 |
| `E_ENV_FILE_INVALID` | .env 文件格式错误 | 检查 .env 文件 |
| `E_TOOL_MISSING` | 依赖工具缺失（如 ffmpeg） | 安装对应工具 |
| `E_MCPORTER_NOT_FOUND` | mcporter 未安装 | `toolkit.py setup` 自动安装 |
| `E_SCRIPT_FAILED` | 脚本执行失败 | 检查具体输出 |

---

## mcporter 自动安装（图片理解 + 联网搜索）

图片理解和联网搜索依赖 `mcporter`。运行一键安装：
```bash
bash scripts/install-mcporter.sh
```

---

## TTS（语音合成）

```bash
# 基本用法
python3 scripts/toolkit.py tts "你好，欢迎使用" -v female-shaonv -o output.mp3

# 可用音色：female-shaonv（少女）、male-qn-qingse（青男）、female-yujie（御姐）等
```

---

## 图片生成

```bash
# 文生图（默认返回 URL，需 --download 才下载）
python3 scripts/toolkit.py image "一张咖啡馆的照片" -o photo.png --download

# 指定比例
python3 scripts/toolkit.py image "山水风景" --aspect-ratio 16:9 -o landscape.png
```

---

## 音乐生成

```bash
# 纯音乐
python3 scripts/toolkit.py music --prompt "ambient electronic, atmospheric" --instrumental -o ambient.mp3

# 带歌词
python3 scripts/toolkit.py music --prompt "轻快流行音乐" --lyrics "[verse]\nHello world" -o song.mp3
```

---

## 视频生成

```bash
# 文生视频（6-10 秒）
python3 scripts/toolkit.py video --prompt "A cat on a moonlit rooftop" -o cat.mp4

# 图生视频
python3 scripts/toolkit.py video --mode i2v --prompt "柔和的风吹过" --first-frame photo.png -o anim.mp4
```

---

## 飞书群管理

```bash
# 列出机器人所在的所有群聊
python3 scripts/toolkit.py feishu list

# 发送文件到群聊（交互式选择群）
python3 scripts/toolkit.py feishu send output.png
```

---

## 诊断工具（直接调用）

```bash
# Agent 推荐：获取完整状态 JSON
python3 scripts/toolkit.py check --json

# 检查单个功能
bash scripts/check.sh --feature tts --json
bash scripts/check.sh --feature mcporter --json

# 首次运行引导
python3 scripts/toolkit.py setup
```
