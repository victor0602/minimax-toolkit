#!/usr/bin/env python3
"""Send local image to Feishu user or chat"""
import sys, requests, json, os

# === 核心配置区（从环境变量读取，敏感信息切勿硬编码） ===
APP_ID = os.environ.get("FEISHU_APP_ID", "")
APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
CHAT_ID = os.environ.get("FEISHU_CHAT_ID", "")
DEFAULT_USER_ID = os.environ.get("FEISHU_DEFAULT_USER_ID", "")

def send_local_image(file_path, to_user=None, to_chat=None):
    # Get token
    res_token = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    token = res_token.get("tenant_access_token")
    if not token:
        print("Token failed:", res_token)
        return
    headers = {"Authorization": f"Bearer {token}"}
    
    # Upload image
    with open(file_path, 'rb') as f:
        files = {"image": (os.path.basename(file_path), f, "image/jpeg")}
        data = {"image_type": "message"}
        res = requests.post("https://open.feishu.cn/open-apis/im/v1/images",
                          headers=headers, data=data, files=files).json()
    
    print("Upload result:", json.dumps(res, indent=2))
    image_key = res.get("data", {}).get("image_key")
    if not image_key:
        print("Failed to get image_key")
        return
    
    # Send message
    if to_user:
        payload = {"receive_id": to_user, "msg_type": "image", "content": json.dumps({"image_key": image_key})}
        rid_type = "open_id"
    elif to_chat:
        payload = {"receive_id": to_chat, "msg_type": "image", "content": json.dumps({"image_key": image_key})}
        rid_type = "chat_id"
    else:
        print("Must specify either to_user or to_chat")
        return
    
    res2 = requests.post(f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={rid_type}",
                       headers=headers, json=payload).json()
    print("Send result:", json.dumps(res2, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python send_feishu_image_local.py <file_path> [open_id]")
        sys.exit(1)
    file_path = sys.argv[1]
    to_user = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_USER_ID
    if not to_user:
        print("[Error] FEISHU_DEFAULT_USER_ID environment variable is not set.")
        print("  Set it in your .env file or export FEISHU_DEFAULT_USER_ID=ou_xxx")
        sys.exit(1)
    send_local_image(file_path, to_user=to_user)
