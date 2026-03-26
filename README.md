# MiniMax Toolkit

MiniMax 全功能工具包，支持语音合成、图片生成、图片理解和联网搜索。

## 更新日志

### v1.1.0 (2026-03-26)

**TTS 脚本重写，优化稳定性：**

- 🔧 **新增直接 API 调用**：当 minimax-multimodal 脚本不可用时，自动 fallback 到直接调用 MiniMax TTS API
- 🐛 **修复音频数据解析**：支持多种响应格式（`data.audio`、`extra_info.audio`、根级别 `audio`）
- 📝 **新增 `--verbose` 模式**：显示详细调用信息，方便调试
- ✨ **新增 `api` 子命令**：直接打印 API 返回的 JSON，便于排查问题
- 💡 **更好的错误提示**：区分不同类型的错误（超时、网络、API 错误等）

**新增调试功能：**

```bash
# 查看详细日志
python3 scripts/tts.py tts "测试" --verbose

# 直接查看 API 返回
python3 scripts/tts.py api "测试"
```

---

### v1.0.0 (2026-03-xx)

初始版本，包含：
- 语音合成 (TTS)
- 图片生成 (image-01)
- 图片理解 (understand_image)
- 联网搜索 (web_search)

## 快速开始

### 语音合成 (TTS)

```bash
# 基本用法
python3 scripts/tts.py tts "你好，欢迎使用" -v female-shaonv -o output.mp3

# 查看详细信息（调试用）
python3 scripts/tts.py tts "测试语音" --verbose

# 直接查看 API 返回的 JSON
python3 scripts/tts.py api "测试文本"
```

**可用语音 ID：**
- `female-shaonv` - 少女音（默认）
- `male-qn-qingse` - 青年男声
- `male-qn-jingying` - 精英男声
- `female-yujie` - 御姐音
- `female-tianmei` - 甜美女声

### 图片生成

```bash
python3 scripts/image_generate.py "一张咖啡馆的照片" -o output.png
```

## 常见问题

### Q: 语音生成失败怎么办？

1. 检查 API Key 是否正确设置：
   ```bash
   echo $MINIMAX_API_KEY
   ```

2. 使用 `--verbose` 查看详细错误信息：
   ```bash
   python3 scripts/tts.py tts "测试" --verbose
   ```

3. 直接查看 API 返回：
   ```bash
   python3 scripts/tts.py api "测试"
   ```

### Q: 提示 "No audio data in response"？

这表示 API 返回了成功状态，但响应中没有音频数据。可能原因：
- API 积分不足
- 文本包含不支持的字符
- API 临时故障

可以尝试：
- 缩短文本长度
- 等待片刻后重试
- 使用 `api` 命令查看完整响应

## 文件结构

```
minimax-toolkit/
├── SKILL.md          # 技能说明文档
├── README.md         # 本文件
└── scripts/
    ├── tts.py        # 语音合成脚本
    └── image_generate.py  # 图片生成脚本
```
