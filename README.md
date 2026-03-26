# MiniMax Toolkit for OpenClaw

 MiniMax 全功能工具包，为 OpenClaw AI 助手打造。支持**图片理解**、**联网搜索**、**语音合成**、**图片生成**四大能力，一键调用。

---

## 功能一览

| 能力 | 模型 | 说明 |
|------|------|------|
| 🖼️ 图片理解 | MiniMax VLM | 识别图片内容，回答问题 |
| 🔍 联网搜索 | MiniMax Search | 搜索新闻、资讯、信息 |
| 🔊 语音合成 | speech-2.8-hd | 高质量 TTS，支持多种音色 |
| 🎨 图片生成 | image-01 | 文生图，支持多种风格 |

---

## 快速开始

### 前置要求

- Python 3.8+
- [OpenClaw](https://github.com/openclaw/openclaw) 已安装
- MiniMax API Key（[获取地址](https://platform.minimaxi.com)）

### 安装

**1. 克隆仓库**
```bash
git clone https://github.com/victor0602/minimax-toolkit.git
cd minimax-toolkit
```

**2. 配置环境变量**

将以下内容添加到你的 shell 配置文件中（`~/.zshrc` 或 `~/.bashrc`）：

```bash
export MINIMAX_API_KEY="sk-cp-你的API密钥"
export MINIMAX_API_HOST="https://api.minimaxi.com"
```

然后执行：
```bash
source ~/.zshrc
```

**3. 安装 Python 依赖（如需）**

```bash
pip install google-generativeai requests websockets ffmpeg-python
```

---

## 使用方法

### 1. 联网搜索

```bash
mcporter call MiniMax.web_search query: "今天北京天气怎么样"
```

**返回示例**：实时搜索结果，包含标题、摘要、链接、日期。

---

### 2. 图片理解

```bash
mcporter call MiniMax.understand_image prompt: "这张图片里有什么？" image_source: "https://example.com/image.jpg"
```

支持的图片来源：
- **公开 URL**：直接传入 URL
- **本地文件**：传入本地路径（如 `/Users/name/photo.jpg`）

---

### 3. 语音合成（TTS）

```bash
cd ~/.openclaw/workspace
python3 scripts/tts.py tts "你好，欢迎使用 MiniMax 语音合成" -v female-shaonv -o output.mp3
```

**参数说明**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `text` | 要合成的文本 | — |
| `-v` | 音色选择 | female-shaonv |
| `-o` | 输出文件路径 | minimax-output/output.mp3 |

**音色列表**（常用）：

| 音色 ID | 说明 |
|--------|------|
| `female-shaonv` | 女声·少女 |
| `female-tianmei` | 女声·甜美 |
| `male-qn-qingse` | 男声·青年 |
| `male-yunyang` | 男声·云扬 |

**完整音色列表**：
```bash
python3 minimax-multimodal/scripts/tts/generate_voice.py list-voices
```

**高级：多段落语音**（适合有声书、播客）：
```bash
# 1. 编写 segments.json
# 2. 生成音频
python3 minimax-multimodal/scripts/tts/generate_voice.py generate segments.json \
  -o output.mp3 --crossfade 200
```

---

### 4. 图片生成

```bash
cd ~/.openclaw/workspace
python3 scripts/image_generate.py "一只在樱花树下打盹的小猫" -o my_image.png
```

生成的图片保存在指定路径，支持 PNG/JPG 格式。

---

## 发送到飞书

如果你使用 OpenClaw 的飞书频道，可以使用以下脚本发送内容：

### 发送图片

```bash
python3 ~/.openclaw/workspace/send_feishu_image_local.py <本地图片路径> [open_id]
```

### 发送语音（opus 格式）

```bash
# 将 MP3 转换为 opus
ffmpeg -i input.mp3 -c:a libopus output.opus -y

# 发送到飞书
python3 ~/.openclaw/workspace/send_feishu_audio.py output.opus
```

> 注意：飞书原生语音（绿色气泡）只支持 .opus 格式，不支持 MP3。

---

## 架构说明

```
minimax-toolkit/
├── SKILL.md              # OpenClaw Skill 定义文件
├── _meta.json           # 元数据
└── scripts/
    ├── tts.py           # TTS 封装脚本
    └── image_generate.py # 图片生成封装脚本
```

- **MCP 工具**（web_search、understand_image）：通过 mcporter 配置全局调用
- **TTS / 图片生成**：封装为独立脚本，方便调用

---

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `MINIMAX_API_KEY` | MiniMax API 密钥（必填） | — |
| `MINIMAX_API_HOST` | API 地址 | `https://api.minimaxi.com` |

---

## 常见问题

**Q: 报 `MINIMAX_API_KEY not set` 错误？**
> 确保已在 shell 配置文件中正确设置 `MINIMAX_API_KEY`，并执行了 `source ~/.zshrc`。

**Q: TTS 报 401 错误？**
> API Key 无效或已过期，请到 [MiniMax 控制台](https://platform.minimaxi.com) 重新获取。

**Q: 图片生成返回 403？**
> 部分图片 URL 需要认证或已过期，请使用公开可访问的图片链接。

**Q: 如何更换音色？**
> 使用 `-v` 参数指定音色 ID，如 `-v female-tianmei`。完整列表参考上文"音色列表"。

---

## 开源协议

MIT License

---

## Star History

如果你觉得这个工具包有帮助，欢迎点一个 ⭐！

https://github.com/victor0602/minimax-toolkit
