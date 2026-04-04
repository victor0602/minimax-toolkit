#!/usr/bin/env python3
"""Send local image to Feishu chat via chat_id (default) or open_id."""
import sys, requests, json, os

# === 核心配置区（从环境变量读取，敏感信息切勿硬编码） ===
APP_ID = os.environ.get("FEISHU_APP_ID", "")
APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
CHAT_ID = os.environ.get("FEISHU_CHAT_ID", "")

def send_local_image(file_path, to_chat=None, to_user=None):
    """发送图片到飞书聊天或用户
    
    Args:
        file_path: 本地图片路径
        to_chat:  chat_id（默认使用 FEISHU_CHAT_ID）
        to_user:   open_id（单独用户）
    """
    if not APP_ID or not APP_SECRET:
        print("[Error] FEISHU_APP_ID or FEISHU_APP_SECRET is not set.")
        print("  Set them in your .env file or export FEISHU_APP_ID and FEISHU_APP_SECRET")
        return False

    # Get token
    res_token = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": APP_ID, "app_secret": APP_SECRET}
    ).json()
    token = res_token.get("tenant_access_token")
    if not token:
        print("Token failed:", res_token)
        return False
    headers = {"Authorization": f"Bearer {token}"}

    # Upload image
    with open(file_path, 'rb') as f:
        files = {"image": (os.path.basename(file_path), f, "image/jpeg")}
        data = {"image_type": "message"}
        res = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/images",
            headers=headers, data=data, files=files
        ).json()

    print("Upload result:", json.dumps(res, indent=2))
    image_key = res.get("data", {}).get("image_key")
    if not image_key:
        print("Failed to get image_key")
        return False

    # Send message — prefer chat_id if target provided, else use FEISHU_CHAT_ID
    if to_user:
        payload = {
            "receive_id": to_user,
            "msg_type": "image",
            "content": json.dumps({"image_key": image_key})
        }
        rid_type = "open_id"
    elif to_chat or CHAT_ID:
        payload = {
            "receive_id": to_chat or CHAT_ID,
            "msg_type": "image",
            "content": json.dumps({"image_key": image_key})
        }
        rid_type = "chat_id"
    else:
        print("[Error] No target: provide to_chat / to_user argument or set FEISHU_CHAT_ID")
        return False

    res2 = requests.post(
        f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={rid_type}",
        headers=headers, json=payload
    ).json()
    print("Send result:", json.dumps(res2, indent=2))
    return res2.get("code") == 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python send_feishu_image.py <file_path>              # 使用 FEISHU_CHAT_ID")
        print("  python send_feishu_image.py <file_path> <chat_id>    # 指定 chat_id")
        print("  python send_feishu_image.py <file_path> --user <open_id>  # 指定 open_id")
        sys.exit(1)

    file_path = sys.argv[1]

    if len(sys.argv) > 3 and sys.argv[2] == "--user":
        to_user = sys.argv[3]
        success = send_local_image(file_path, to_user=to_user)
    elif len(sys.argv) > 2:
        success = send_local_image(file_path, to_chat=sys.argv[2])
    else:
        success = send_local_image(file_path)

    sys.exit(0 if success else 1)
