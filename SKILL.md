---
name: minimax-toolkit
description: MiniMax 全功能工具包。处理图片理解（understand_image）、联网搜索（web_search）、语音合成（TTS）、图片生成（image-01）时激活。触发词：生成图片、搜索、语音合成、图片理解、联网查询。
---

# MiniMax 全功能工具包

## 工具总览

| 能力 | 调用方式 | 说明 |
|------|---------|------|
| 图片理解 | `mcporter call MiniMax.understand_image` | 识别图片内容 |
| 联网搜索 | `mcporter call MiniMax.web_search` | 搜索新闻/信息 |
| 语音合成 | `python3 scripts/tts.py tts "<文本>"` | 生成 MP3 语音 |
| 图片生成 | `python3 scripts/image_generate.py "<prompt>"` | 生成图片 |

---

## 1. 图片理解（understand_image）

通过 MiniMax MCP 工具调用，支持 URL 和本地文件。

```
mcporter call MiniMax.understand_image prompt: "描述这张图片" image_source: "图片URL或本地路径"
```

**示例**：
```bash
mcporter call MiniMax.understand_image prompt: "这张图片里有什么？" image_source: "https://example.com/image.jpg"
```

**注意**：MCP 工具走 mcporter 调用，无需额外安装。

---

## 2. 联网搜索（web_search）

通过 MiniMax MCP 工具调用。

```
mcporter call MiniMax.web_search query: "搜索内容"
```

**示例**：
```bash
mcporter call MiniMax.web_search query: "今天北京天气"
```

---

## 3. 语音合成（TTS）

使用 MiniMax speech-2.8-hd 模型生成语音。

### 依赖环境变量
```
MINIMAX_API_KEY=sk-cp-...
MINIMAX_API_HOST=https://api.minimaxi.com
```

### 基本用法
```bash
cd ~/.openclaw/workspace
python3 ~/.openclaw/workspace/skills/minimax-toolkit/scripts/tts.py tts "你好，欢迎使用" -v female-shaonv -o minimax-output/output.mp3
```

### 转换为 opus（飞书原生语音）
```bash
ffmpeg -i minimax-output/output.mp3 -c:a libopus minimax-output/output.opus -y
```

### 发送语音到飞书
```bash
python3 ~/.openclaw/workspace/send_feishu_audio.py minimax-output/output.opus
```

### 常见问题排查

**问题：API 调用成功但没有生成音频文件**
- 检查是否返回 `No audio data returned from API` 错误
- 检查 `extra_info` 中是否有 audio 字段
- 确认 API Key 是否有 TTS 权限

**问题：积分消耗但语音生成失败**
- 可能是 API 限流或临时故障，重试可能成功
- 检查网络连接是否稳定

---

## 4. 图片生成（image-01）

调用 MiniMax image-01 模型生成图片。

### 基本用法
```bash
cd ~/.openclaw/workspace
python3 ~/.openclaw/workspace/skills/minimax-toolkit/scripts/image_generate.py "一张咖啡馆的照片" -o minimax-output/photo.png
```

### 发送图片到飞书
```bash
python3 ~/.openclaw/workspace/send_feishu_image_local.py minimax-output/photo.png
```

**API 端点**：`POST https://api.minimaxi.com/v1/image_generation`

---

## 发送工具（通用）

### 语音发送（飞书绿色气泡）
脚本：`~/.openclaw/workspace/send_feishu_audio.py`
```bash
python3 ~/.openclaw/workspace/send_feishu_audio.py <本地音频路径>
```
支持 .mp3 和 .opus 格式。

### 图片发送
脚本：`~/.openclaw/workspace/send_feishu_image_local.py`
```bash
python3 ~/.openclaw/workspace/send_feishu_image_local.py <本地图片路径> [open_id]
```
自动上传到飞书换取 image_key 并发送。

---

## 环境配置

MiniMax API Key 和 Host 通过环境变量传入：
- `MINIMAX_API_KEY` - API Key（sk-cp- 开头）
- `MINIMAX_API_HOST` - API 地址（默认 https://api.minimaxi.com）

MCP 工具（web_search / understand_image）通过 `~/.mcporter/mcporter.json` 配置，已经全局配置好了，可以直接用 `mcporter call` 调用。