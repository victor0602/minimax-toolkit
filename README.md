# MiniMax Toolkit

**OpenClaw 原生 · 多模态能力工具包**

[![GitHub stars](https://img.shields.io/github/stars/victor0602/minimax-toolkit)](https://github.com/victor0602/minimax-toolkit)
[![License MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

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
| 🎬 **Video** | Hailuo-2.3 | 文生视频 / 图生视频 / 首尾帧 |
| 🎵 **Music** | music-2.5 | 歌词+旋律 或 纯音乐 |
| 📨 **Feishu** | — | 图片/音频/视频气泡推送 |

---

## 快速开始

```bash
# 克隆项目
git clone https://github.com/victor0602/minimax-toolkit.git
cd minimax-toolkit

# 运行首次配置引导
python3 scripts/toolkit.py setup

# 非交互模式（使用已有环境变量）
python3 scripts/toolkit.py setup --non-interactive

# 验证环境
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

### 飞书消息发送（独立脚本）

独立脚本可独立运行，不依赖 `toolkit.py`：

```bash
# 发送图片（支持 chat_id / open_id）
python3 send_feishu_image.py cat.png
python3 send_feishu_image.py cat.png --user ou_xxxxxxxx

# 发送音频
#  原生语音（绿色气泡，需 .opus 格式，MP3 会自动转换）
python3 send_feishu_audio.py voice.mp3
#  文件形式（带播放器）
python3 send_feishu_audio.py voice.mp3 file

# 发送视频
#  原生气泡（封面 + mp4， 推荐）
python3 send_feishu_native_video.py video.mp4
#  文件形式（带播放器）
python3 send_feishu_video.py video.mp4
```

> 注意：音频必须为 `.opus` 格式（MP3 会自动转）；视频原生气泡需 ffmpeg 抽取首帧作为封面。

---

## 可用音色

| ID | 名称 |
|----|------|
| `female-shaonv` | 少女 |
| `female-yujie` | 御姐 |
| `female-baihe` | 百合 |
| `female-jingying` | 京莺 |
| `male-yuanbin` | 元彬 |
| `male-qn-qingse` | 青男 |

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
├── _meta.json                 # 元数据（版本信息）
├── .env.example               # 环境变量模板
├── .gitignore                 # Git 忽略配置
├── docs/
│   └── architecture.svg      # 系统架构图
├── scripts/
│   ├── toolkit.py             # 统一 CLI 入口
│   ├── setup.sh               # 首次配置引导
│   ├── check.sh               # 诊断检查
│   ├── test_env.py            # 环境测试
│   ├── test_features.py       # 功能测试
│   ├── lib/
│   │   ├── common.sh          # 共享函数（load_env, check_api_key）
│   │   ├── diagnose.sh        # 诊断函数库
│   │   └── feishu.py         # 飞书 API 共享库（FeishuAPI 类）
│   ├── tts.py / tts/          # 语音合成
│   ├── image_generate.py / image/  # 图片生成
│   ├── music/                 # 音乐生成
│   ├── video/                 # 视频生成
│   └── install-mcporter.sh    # mcporter 安装
└── send_feishu_*.py           # 飞书消息发送工具（独立脚本）
    ├── send_feishu_audio.py   # 发送音频（原生语音 or 文件形式）
    ├── send_feishu_image.py    # 发送图片
    ├── send_feishu_video.py    # 发送视频（文件形式）
    └── send_feishu_native_video.py  # 发送视频（原生气泡，含封面）
```

---

## 更新日志

### v1.5.4 (2026-04-05)

**安全：**
- 🔧 **curl|sh pipe 修复**：`install-mcporter.sh` 改为下载到临时文件再执行，避免中间人攻击
- 🔧 **临时文件泄漏修复**：`generate_long_video.sh` 新增 `trap` 处理器，脚本退出或中断时自动清理临时目录
- 🔧 **MIT License 头**：所有 Python/Shell 源文件新增许可证头

**运维：**
- ✨ **新增 SECURITY.md**：安全漏洞报告流程和已知安全考虑
- ✨ **新增 requirements.txt**：Python 依赖版本锁定

### v1.5.3 (2026-04-05)

**安全：**
- 🔧 **路径穿越防护**：新增 `validate_output_path()` 函数，`generate_video.sh` / `add_bgm.sh` / `generate_music.sh` 输出路径均做校验

**修复：**
- 🔧 **setup.sh TTY 检测 bug**：`if [[ ! is_tty ]]` → `if ! is_tty`，非交互模式检测恢复正常
- 🔧 **test_features.py WARN 未定义**：新增 `WARN` 常量（黄色警告符号）
- 🔧 **generate_music.sh 空 lyrics**：非纯音乐模式必须传入歌词，否则报错退出
- 🔧 **jq || true 静默错误**：统一改为 `jq '...' || var=fallback`，错误不再被吞掉
- 🔧 **ffmpeg 静默失败**：concat demuxer fallback 失败时正确报错退出
- 🔧 **cmd_check_env 死链接**：指向不存在的 `check_environment.sh`，改为调用 `scripts/check.sh`
- 🔧 **FeishuAPI 补全**：新增 `list_chats()` 方法
- 🔧 **cmd_tts 新增 --model 参数**：传递给底层 `generate_voice.sh`

**改进：**
- ✨ **新增 --version 标志**：`python3 scripts/toolkit.py --version` 输出版本号
- ✨ **新增 CONTRIBUTING.md**：开源贡献指南
- 📖 **SKILL.md 去重**：删除重复的"视频生成"章节
- 🔧 **依赖补全**：`diagnose.sh` 依赖列表新增 `bc`（用于音视频时长计算）

### v1.5.2 (2026-04-05)

**重构：**
- 🔧 **cmd_feishu 重构**：删除 ~110 行内联重复代码，改用 `FeishuAPI` 共享库
- 🔧 **FeishuAPI 补全**：新增 `list_chats()` 方法，群聊列表功能统一

**修复：**
- 🔧 **doctor --fix .env 创建**：现在同时包含 Feishu 环境变量（FEISHU_APP_ID / FEISHU_APP_SECRET / FEISHU_CHAT_ID）
- 🔧 **JSON 输出修复**：`diagnose.sh` / `common.sh` 的 `echo|jq` 改为 `printf '%s'|jq`，消除值末多余 `\n`
- 🔧 **diagnose.sh 清理**：删除重复的 `local key_type` 声明

**文档：**
- 📖 **SKILL.md 补全**：新增飞书命令文档（`feishu list` / `feishu send`）和环境变量说明

### v1.5.1 (2026-04-04)

**重构：**
- 🔧 **飞书发送脚本重构**：统一使用 `scripts/lib/feishu.py` 共享库（FeishuAPI 类）
- 🔧 **错误处理修复**：`send_feishu_audio.py` 不再虚假打印"发送成功"
- 🔧 **合并冗余**：`send_feishu_image_local.py` 合并至 `send_feishu_image.py`
- 🔧 **视频脚本修复**：封面上传失败时正确中断，不再虚假继续

### v1.5.0 (2026-04-04)

**新功能：**
- 🚀 **doctor 命令**：环境诊断 + `--fix` 自动修复
- 🎯 **首次运行检测**：未配置时自动提示引导
- 📋 **feishu 群管理**：`feishu list` / `feishu send`
- 📊 **系统架构图**：SVG 彩色架构图
- 🧪 **测试套件**：`test_env.py` / `test_features.py`

**改进：**
- 🔧 **setup.sh 增强**：检测现有环境变量，询问确认使用
- 🔧 **精准错误码**：所有错误返回 `E_*` 码 + 修复建议
- 🔧 **Music 超时处理**：服务器延迟时 Skip 而非 FAIL
- 🔧 **跨平台兼容**：修复 macOS `date` 和 bash 3.2 兼容性问题
- 🔧 **setup --non-interactive**：支持非交互模式

---

### v1.4.0 (2026-03-23)

- 🚀 **统一 CLI `toolkit.py`**：所有功能单一入口
- 📊 **结构化诊断**：`check --json` 机器可读输出
- 🔍 **精确错误码**：结构化错误信息

---

## License

MIT
