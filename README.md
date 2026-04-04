# MiniMax Toolkit

**OpenClaw 原生 · 多模态能力工具包**

为 OpenClaw Agent 深度适配的 MiniMax 多功能工具包，支持语音合成、图片生成、视频生成、音乐生成，以及飞书消息推送。

---

## 系统架构

![Architecture](./docs/architecture.svg)

---

## 核心功能

| 功能 | 模型 | 说明 |
|------|------|------|
| 🎙 **TTS** | speech-2.8-hd | 语音合成，支持多种音色 |
| 🎨 **Image** | image-01 | 文生图 / 图生图 |
| 🎬 **Video** | MiniMax-Hailuo-2.3 | 文生视频 / 图生视频 / 首尾帧 |
| 🎵 **Music** | music-2.5 | 歌词+旋律 或 纯音乐 |
| 📨 **Feishu** | — | 图片/音频/视频气泡推送 |

---

## 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/victor0602/minimax-toolkit.git
cd minimax-toolkit

# 2. 复制配置模板
cp .env.example .env
# 编辑 .env，填入你的 MINIMAX_API_KEY

# 3. 运行首次配置引导
python3 scripts/toolkit.py setup

# 4. 验证环境
python3 scripts/toolkit.py doctor --fix
```

---

## 统一 CLI

```bash
# 查看环境状态（Agent 推荐）
python3 scripts/toolkit.py check --json

# 环境诊断 + 自动修复
python3 scripts/toolkit.py doctor --fix

# 查看当前配置
python3 scripts/toolkit.py env --show

# 设置 API Key
python3 scripts/toolkit.py env --key sk-cp-your-key-here
```

### 语音合成 (TTS)

```bash
python3 scripts/toolkit.py tts "你好世界" -v female-shaonv -o output.mp3
```

### 图片生成 (Image)

```bash
# 仅返回 URL
python3 scripts/toolkit.py image "一只橘色的猫" -o cat.png

# 下载到本地
python3 scripts/toolkit.py image "一只橘色的猫" -o cat.png --download
```

### 音乐生成 (Music)

```bash
# 纯音乐
python3 scripts/toolkit.py music --prompt "ambient electronic" --instrumental -o ambient.mp3

# 带歌词
python3 scripts/toolkit.py music --prompt "upbeat pop" --lyrics "hello world" -o song.mp3
```

### 视频生成 (Video)

```bash
# 文生视频
python3 scripts/toolkit.py video --prompt "一只猫在月光下的屋顶上" -o cat.mp4

# 图生视频
python3 scripts/toolkit.py video --prompt "一只猫在奔跑" --first-frame cat.png -o cat_video.mp4
```

### 飞书群管理

```bash
# 列出所有可用的群聊
python3 scripts/toolkit.py feishu list

# 发送文件到选定的群聊
python3 scripts/toolkit.py feishu send output.png
```

---

## 可用音色

| ID | 名称 |
|----|------|
| `female-shaonv` | 少女 |
| `male-qn-qingse` | 青男 |
| `female-yujie` | 御姐 |
| `male-yuanbin` | 元彬 |
| `female-baihe` | 百合 |
| `female-jingying` | 京莺 |

---

## mcporter（图片理解 + 联网搜索）

```bash
# 安装
bash scripts/install-mcporter.sh

# 重启 OpenClaw Gateway
openclaw gateway restart

# 验证
mcporter list

# 图片理解
mcporter call MiniMax.understand_image prompt: "描述这张图片" image_source: "https://example.com/image.jpg"

# 联网搜索
mcporter call MiniMax.web_search query: "今天北京的天气"
```

---

## 测试

```bash
# 环境完整性测试
python3 scripts/test_env.py

# 功能完整性测试
python3 scripts/test_features.py
```

---

## 项目结构

```
minimax-toolkit/
├── SKILL.md                    # OpenClaw 技能说明
├── README.md                   # 本文件
├── .env.example                # 环境变量模板
├── docs/
│   └── architecture.svg        # 系统架构图
└── scripts/
    ├── toolkit.py             # 统一 CLI 入口
    ├── setup.sh               # 首次配置引导
    ├── check.sh               # 诊断检查
    ├── test_env.py            # 环境测试
    ├── test_features.py       # 功能测试
    ├── lib/
    │   ├── common.sh          # 共享函数（load_env, check_api_key）
    │   └── diagnose.sh       # 诊断函数库
    ├── tts.py / tts/          # 语音合成
    ├── image_generate.py / image/  # 图片生成
    ├── music/                 # 音乐生成
    ├── video/                 # 视频生成
    └── install-mcporter.sh    # mcporter 安装
```

---

## 更新日志

### v1.5.0 (2026-04-04)

**新功能：**
- 🚀 **doctor 命令**：环境诊断 + `--fix` 自动修复
- 🎯 **首次运行检测**：未配置时自动提示引导
- 📋 **feishu 群管理**：`feishu list` / `feishu send`
- 📊 **系统架构图**：SVG 彩色架构图

**改进：**
- 🔧 **setup.sh 增强**：检测现有环境变量，询问确认使用
- 🔧 **精准错误码**：所有错误返回 `E_*` 码 + 修复建议
- 🔧 **Music 超时处理**：服务器延迟时 Skip 而非 FAIL

---

### v1.4.0 (2026-03-23)

- 🚀 **统一 CLI `toolkit.py`**：所有功能单一入口
- 📊 **结构化诊断**：`check --json` 机器可读输出
- 🔍 **精确错误码**：结构化错误信息

---

## License

MIT
