---
name: minimax-toolkit
description: MiniMax 全功能工具包。处理图片理解（understand_image）、联网搜索（web_search）、语音合成（TTS）、图片生成（image-01）、音乐生成（music-2.5）、视频生成（MiniMax-Hailuo-2.3）时激活。触发词：生成图片、搜索、语音合成、图片理解、联网查询、生成音乐、生成视频。
---

# MiniMax 全功能工具包

## 工具总览

| 能力 | 调用方式 | 说明 |
|------|---------|------|
| 图片理解 | `mcporter call MiniMax.understand_image` | 识别图片内容 |
| 联网搜索 | `mcporter call MiniMax.web_search` | 搜索新闻/信息 |
| 语音合成 | `python3 scripts/tts.py tts "<文本>"` | 生成 MP3 语音 |
| 图片生成 | `python3 scripts/image_generate.py "<prompt>"` | 生成图片 |
| 音乐生成 | `bash scripts/music/generate_music.sh` | 生成音乐 |
| 视频生成 | `bash scripts/video/generate_video.sh` | 生成视频 |

---

## 环境配置

所有 MiniMax API 能力依赖以下环境变量（在 `.env` 或 shell 中设置）：

| 变量 | 说明 | 示例 |
|------|------|------|
| `MINIMAX_API_KEY` | MiniMax API Key | `sk-cp-xxxxx` 或 `sk-api-xxxxx` |
| `MINIMAX_API_HOST` | API 地址（默认中国大陆） | `https://api.minimaxi.com` |

**注意**：`mcporter` 配置的 MCP 工具（web_search / understand_image）有独立的全局配置，无需在 skill 内设置。

---

## mcporter 自动安装（图片理解 + 联网搜索）

图片理解和联网搜索依赖 `mcporter`。运行一键安装脚本即可：

```bash
bash ~/.openclaw/workspace/skills/minimax-toolkit/scripts/install-mcporter.sh
```

脚本会自动完成：
1. 检测/安装 `uvx`（MCP 服务器运行环境）
2. 检测/安装 `mcporter` CLI
3. 引导输入 MiniMax API Key
4. 创建/更新 `~/.openclaw/workspace/config/mcporter.json`
5. 验证配置是否生效

**注意**：安装完成后建议重启 OpenClaw Gateway 使配置生效：

```bash
openclaw gateway restart
```

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

### 基本用法
```bash
cd ~/.openclaw/workspace
python3 ~/.openclaw/workspace/skills/minimax-toolkit/scripts/tts.py tts "你好，欢迎使用" -v female-shaonv -o minimax-output/output.mp3
```

### 转换为 opus（飞书原生语音）
```bash
ffmpeg -i minimax-output/output.mp3 -c:a libopus minimax-output/output.opus -y
```

---

## 4. 图片生成（image-01）

调用 MiniMax image-01 模型生成图片。

### 基本用法
```bash
cd ~/.openclaw/workspace
python3 ~/.openclaw/workspace/skills/minimax-toolkit/scripts/image_generate.py "一张咖啡馆的照片" -o minimax-output/photo.png --download
```
> 注意：`--download` 需显式传入才会下载图片文件，默认为 URL 模式。

**API 端点**：`POST https://api.minimaxi.com/v1/image_generation`

---

## 5. 音乐生成（music-2.5）

使用 `music-2.5` 模型生成音乐。

### 基本用法
```bash
cd ~/.openclaw/workspace
mkdir -p minimax-output

bash ~/.openclaw/workspace/skills/minimax-toolkit/scripts/music/generate_music.sh \
  --model "music-2.5" \
  --lyrics "[verse]\n你的歌词" \
  --prompt "轻快流行音乐，夜晚主题" \
  --output minimax-output/song.mp3 \
  --download
```

### 关键说明
- **Token Plan Key（sk-cp-）** 支持 `music-2.5` 模型，部分网络环境需加 `--noproxy '*'` 直连
- **API Key（sk-api-）** 支持 `music-2.5+`，也可尝试 `music-2.5`
- 音乐 API 对代理处理有问题，如遇超时，重试即可

### Instrumental 模式（纯音乐，无人声）
```bash
bash ~/.openclaw/workspace/skills/minimax-toolkit/scripts/music/generate_music.sh \
  --model "music-2.5" \
  --instrumental \
  --prompt "ambient electronic, atmospheric" \
  --output minimax-output/ambient.mp3 \
  --download
```

---

## 6. 视频生成（MiniMax-Hailuo-2.3）

使用 `MiniMax-Hailuo-2.3` 模型生成 6~10 秒视频。

### 基本用法
```bash
cd ~/.openclaw/workspace
mkdir -p minimax-output

bash ~/.openclaw/workspace/skills/minimax-toolkit/scripts/video/generate_video.sh \
  --mode t2v \
  --prompt "A cat walks on a moonlit rooftop, [跟随] tracking shot, cinematic lighting" \
  --duration 6 \
  --output minimax-output/video.mp4
```

### 视频参数说明
| 参数 | 值 |
|------|-----|
| 默认模型 | MiniMax-Hailuo-2.3 |
| 默认时长 | 6 秒 |
| 默认分辨率 | 768P |
| 模式 | t2v（文生视频）, i2v（图生视频）, sef（首尾帧） |

### 图生视频（i2v）
```bash
bash ~/.openclaw/workspace/skills/minimax-toolkit/scripts/video/generate_video.sh \
  --mode i2v \
  --first-frame minimax-output/photo.png \
  --prompt "The scene begins to move gently, petals sway in the breeze" \
  --duration 6 \
  --output minimax-output/video_from_photo.mp4
```

---

## 常见问题排查

### TTS：API 调用成功但没有生成音频文件
- 检查是否返回 `No audio data returned from API` 错误
- 检查 `extra_info` 中是否有 audio 字段
- 确认 API Key 是否有 TTS 权限（需 sk-cp- Token Plan Key）

### 音乐：请求超时
- 音乐 API 对代理处理有问题，生成时加 `--noproxy '*'`
- 或配置直连网络后重试

### 视频：生成失败
- 确认 `MINIMAX_API_KEY` 为 Token Plan Key（sk-cp- 开头）
- 检查网络连接是否稳定

### mcporter：MiniMax 工具无法调用
- 确认 `mcporter list` 能看到 MiniMax 服务器且状态健康
- 确认 API Key 有效（sk-cp- 开头为 Token Plan Key）
- 重启 OpenClaw Gateway：`openclaw gateway restart`
