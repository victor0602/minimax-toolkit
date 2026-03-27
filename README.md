# MiniMax Toolkit

**OpenClaw + 飞书专属的 MiniMax 多功能工具包**

> 官方 minimax-multimodal-toolkit 的「OpenClaw 深度适配增强版」，专为飞书 + OpenClaw 工作流打造。

---

## 核心亮点

**🤝 OpenClaw 深度适配**
- SKILL.md 触发词专为 OpenClaw Agent 调度逻辑优化，接入零门槛
- mcporter 集成图片理解 + 联网搜索，官方版没有这两个功能

**📤 飞书原生支持**
- 内置 `send_feishu_audio` / `send_feishu_image` / `send_feishu_native_video` 外挂脚本
- 生成内容直发飞书，图片/音频/视频一键气泡推送，官方版完全没有

**🛡️ 安全性更高**
- 动态路径，无硬编码用户名
- `.gitignore` 防误提交，`.env.example` 模板零配置上手
- `load_env()` 只读取必要变量，不会有多余 secrets 泄露到脚本环境

**🔄 容错机制**
- `tts.py` 主路径失败自动 fallback 直接调 API，不用担心脚本缺失
- 完整 error handling，区分超时 / 网络 / API 错误

---

## 功能对比

| | 官方版 | minimax-toolkit |
|---|---|---|
| TTS / 声音克隆 / 声音设计 | ✅ | ✅ |
| 图片生成（文生图 / 图生图） | ✅ | ✅ |
| 视频生成（文生视频 / 图生视频 / 首尾帧） | ✅ | ✅ |
| 音乐生成 | ✅ | ✅ |
| 媒体处理（格式转换/拼接/裁剪） | ✅ | — |
| 图片理解 + 联网搜索 | ❌ | ✅ via mcporter |
| 飞书推送（图片/音频/视频气泡） | ❌ | ✅ |
| `.env.example` 新手模板 | ❌ | ✅ |
| OpenClaw 触发词优化 | ❌ | ✅ |
| 安全性（动态路径 + 防泄露） | ⚠️ | ✅ |

---

## 安装方式

```bash
# 方式一：直接 git clone
git clone https://github.com/victor0602/minimax-toolkit.git
cd minimax-toolkit
cp .env.example .env
# 编辑 .env，填入你的 MINIMAX_API_KEY

# 方式二：通过 ClawHub 安装
clawhub install minimax-toolkit --workdir ~/.openclaw/workspace --dir skills
```

---

## 更新日志

### v1.2.0 (2026-03-27)

**新增功能：**
- 🎵 **音乐生成**：支持 `music-2.5` 模型，可生成纯音乐或带歌词的歌曲
- 🎬 **视频生成**：支持 `MiniMax-Hailuo-2.3` 模型，文生视频 / 图生视频 / 首尾帧

**代码优化：**
- TTS 和图片生成脚本改为纯自包含，不依赖外部技能包
- 所有脚本移除了硬编码路径，兼容 macOS / Linux / Windows
- 新增 `.env.example` 模板文件，方便其他用户快速配置
- 新增 `.gitignore` 避免误提交 `.env` 和输出文件

**文档完善：**
- SKILL.md 新增完整的 mcporter 安装配置说明
- 修正音乐 API Key 说明（sk-cp- 和 sk-api- 的正确用途）

---

### v1.1.0 (2026-03-26)

- TTS 脚本重写，增加直接 API 调用 fallback
- 修复音频数据解析（支持多种响应格式）
- 新增 `--verbose` 模式和 `api` 子命令

---

## 关于本工具包

MiniMax Toolkit 是面向 OpenClaw Agent 的 MiniMax 多模态能力集成工具，包含六大功能：

| 功能 | 模型 | 说明 |
|------|------|------|
| 语音合成 | speech-2.8-hd | 支持多种音色和情绪调节 |
| 图片生成 | image-01 | 文生图 / 图生图（角色一致性） |
| 图片理解 | - | 通过 mcporter MCP 工具调用 |
| 联网搜索 | - | 通过 mcporter MCP 工具调用 |
| 音乐生成 | music-2.5 / music-2.5+ | 纯音乐或有词歌曲 |
| 视频生成 | MiniMax-Hailuo-2.3 | 文生视频 / 图生视频 / 首尾帧 |

## 快速开始

### 环境配置

1. 复制环境变量模板：
   ```bash
   cp .env.example .env
   # 编辑 .env，填入你的 MINIMAX_API_KEY
   ```

2. 如果需要图片理解或联网搜索，安装 mcporter：
   ```bash
   npm install -g @openwhatsapp/mcporter
   # 然后在 ~/.mcporter/mcporter.json 中配置 MiniMax MCP 服务
   ```

### 语音合成

```bash
python3 scripts/tts.py tts "你好，欢迎使用" -v female-shaonv -o output.mp3
```

**可用音色：** `female-shaonv`（少女）、`male-qn-qingse`（青男）、`female-yujie`（御姐）等

### 图片生成

```bash
python3 scripts/image_generate.py "一张咖啡馆的照片" -o output.png
```

### 音乐生成

```bash
# 纯音乐
bash scripts/music/generate_music.sh --instrumental --prompt "ambient electronic" -o ambient.mp3 --download

# 带歌词
bash scripts/music/generate_music.sh --lyrics "[verse]\nHello world" --prompt "upbeat pop" -o song.mp3 --download
```

### 视频生成

```bash
bash scripts/video/generate_video.sh --mode t2v --prompt "A cat on a moonlit rooftop, [跟随] tracking shot" --duration 6 -o video.mp4
```

## 文件结构

```
minimax-toolkit/
├── SKILL.md                # 技能说明文档（OpenClaw 用）
├── README.md               # 本文件
├── .env.example            # 环境变量模板
├── .gitignore              # Git 忽略配置
└── scripts/
    ├── tts.py             # 语音合成入口
    ├── tts/generate_voice.sh
    ├── image_generate.py   # 图片生成入口
    ├── image/generate_image.sh
    ├── music/generate_music.sh
    └── video/
        ├── generate_video.sh        # 视频生成
        ├── generate_long_video.sh  # 长视频
        ├── generate_template_video.sh
        └── add_bgm.sh
```
