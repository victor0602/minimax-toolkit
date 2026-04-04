#!/usr/bin/env python3
"""
以文件形式发送视频（带播放器，绕过 video 权限限制）
  python3 send_feishu_video.py <video_file>
"""
import sys
import os
import scripts.lib.feishu as feishu

CHAT_ID = os.environ.get("FEISHU_CHAT_ID", "")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 send_feishu_video.py <video_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"[Error] 文件不存在: {file_path}")
        sys.exit(1)

    receive_id = os.environ.get("FEISHU_CHAT_ID", "")
    if not receive_id:
        print("[Error] FEISHU_CHAT_ID is not set.")
        sys.exit(1)

    api = feishu.FeishuAPI()
    if not api.check_config():
        sys.exit(1)

    file_key = api.upload_file(file_path, "stream")
    if not file_key:
        sys.exit(1)

    res = api.send_file(receive_id, file_key)
    if not res:
        sys.exit(1)

    print("[OK] 视频文件发送成功")
    sys.exit(0)
