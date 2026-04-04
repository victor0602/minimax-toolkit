#!/usr/bin/env python3
"""
发送图片到飞书
  python3 send_feishu_image.py <file>                        # 使用 FEISHU_CHAT_ID
  python3 send_feishu_image.py <file> <chat_id>             # 指定 chat_id
  python3 send_feishu_image.py <file> --user <open_id>      # 指定 open_id
"""
import sys
import os
import scripts.lib.feishu as feishu

CHAT_ID = os.environ.get("FEISHU_CHAT_ID", "")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 send_feishu_image.py <file>                   # 使用 FEISHU_CHAT_ID")
        print("  python3 send_feishu_image.py <file> <chat_id>          # 指定 chat_id")
        print("  python3 send_feishu_image.py <file> --user <open_id>    # 指定 open_id")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"[Error] 文件不存在: {file_path}")
        sys.exit(1)

    to_user, to_chat, rid_type = None, None, "chat_id"
    if len(sys.argv) > 3 and sys.argv[2] == "--user":
        to_user, rid_type = sys.argv[3], "open_id"
    elif len(sys.argv) > 2:
        to_chat, rid_type = sys.argv[2], "chat_id"

    receive_id = to_user or to_chat or CHAT_ID
    if not receive_id:
        print("[Error] No target: pass chat_id / open_id or set FEISHU_CHAT_ID")
        sys.exit(1)

    api = feishu.FeishuAPI()
    if not api.check_config():
        sys.exit(1)

    image_key = api.upload_image(file_path)
    if not image_key:
        sys.exit(1)

    res = api.send_image(receive_id, image_key, rid_type)
    if not res:
        sys.exit(1)

    print("[OK] 图片发送成功")
    sys.exit(0)
