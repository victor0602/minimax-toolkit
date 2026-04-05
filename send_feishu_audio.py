#!/usr/bin/env python3
# MIT License — Copyright (c) 2026 Victor
# https://github.com/victor0602/minimax-toolkit

"""
发送音频到飞书
  python3 send_feishu_audio.py <file>           # 原生语音（绿色气泡，.opus）
  python3 send_feishu_audio.py <file> file      # 文件形式（带播放器）
"""
import sys
import os
import subprocess
import tempfile
import scripts.lib.feishu as feishu

CHAT_ID = os.environ.get("FEISHU_CHAT_ID", "")


def convert_to_opus(input_path):
    """用 ffmpeg 将音频转为 .opus 格式，返回临时文件路径；失败返回 None"""
    tmp = tempfile.NamedTemporaryFile(suffix=".opus", delete=False)
    tmp.close()
    r = subprocess.run(
        ["ffmpeg", "-i", input_path, "-c:a", "libopus", "-b:a", "128k", "-y", tmp.name],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"[Error] 转换为 .opus 失败: {r.stderr}")
        os.unlink(tmp.name)
        return None
    return tmp.name


def send_as_voice(api, file_path, receive_id):
    """原生语音（绿色气泡）"""
    opus_path = convert_to_opus(file_path)
    if not opus_path:
        return False
    print(f"[Info] .opus 转换完成: {opus_path}")

    file_key = api.upload_file(opus_path, "opus")
    os.unlink(opus_path)
    if not file_key:
        return False

    res = api.send_audio(receive_id, file_key)
    if not res:
        return False
    print("[OK] 原生语音发送成功")
    return True


def send_as_file(api, file_path, receive_id):
    """文件形式（带播放器）"""
    file_key = api.upload_file(file_path, "stream")
    if not file_key:
        return False

    res = api.send_file(receive_id, file_key)
    if not res:
        return False
    print("[OK] 音频文件发送成功")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 send_feishu_audio.py <file>        # 原生语音（绿色气泡）")
        print("  python3 send_feishu_audio.py <file> file   # 文件形式（带播放器）")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"[Error] 文件不存在: {file_path}")
        sys.exit(1)

    mode = sys.argv[2] if len(sys.argv) > 2 else "voice"
    receive_id = os.environ.get("FEISHU_CHAT_ID", "")
    if not receive_id:
        print("[Error] FEISHU_CHAT_ID is not set.")
        sys.exit(1)

    api = feishu.FeishuAPI()
    if not api.check_config():
        sys.exit(1)

    if mode == "file":
        ok = send_as_file(api, file_path, receive_id)
    else:
        ok = send_as_voice(api, file_path, receive_id)

    sys.exit(0 if ok else 1)
