import sys
import requests
import json
import os

# === 核心配置区 ===
APP_ID = "REDACTED_APP_ID"
APP_SECRET = "REDACTED_APP_SECRET"  # 飞书机器人的 Secret
CHAT_ID = "REDACTED_CHAT_ID_2" # 你的专属对话框 ID

def send_video_as_file(file_path):
    if not os.path.exists(file_path):
        print(f"找不到视频文件: {file_path}")
        return

    # 1. 获取飞书授权 Token
    print("正在获取授权 Token...")
    url_token = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res_token = requests.post(url_token, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    token = res_token.get("tenant_access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # 2. 将视频作为"普通流文件"上传到飞书
    print("正在上传视频文件到飞书服务器...")
    url_upload = "https://open.feishu.cn/open-apis/im/v1/files"
    with open(file_path, 'rb') as f:
        data = {"file_type": "stream", "file_name": os.path.basename(file_path)}
        files = {"file": f}
        res_upload = requests.post(url_upload, headers=headers, data=data, files=files).json()

    print("上传结果:", json.dumps(res_upload, indent=2))
    file_key = res_upload.get("data", {}).get("file_key")
    if not file_key:
        print("视频文件上传失败:", res_upload)
        return

    # 3. 以"文件卡片"形式精准推送到你的聊天框
    print("正在发送视频卡片...")
    url_send = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    payload = {
        "receive_id": CHAT_ID,
        "msg_type": "file",  # 核心：使用 file 类型绕过 video 权限检查
        "content": json.dumps({"file_key": file_key})
    }
    res_send = requests.post(url_send, headers=headers, json=payload).json()
    print("任务完成！发送结果:", json.dumps(res_send, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("错误：请提供本地视频文件的路径。")
        sys.exit(1)
    send_video_as_file(sys.argv[1])
