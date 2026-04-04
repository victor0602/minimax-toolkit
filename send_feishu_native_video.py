import sys
import requests
import json
import os
import subprocess

# === 核心配置区 ===
APP_ID = "REDACTED_APP_ID"
APP_SECRET = "REDACTED_APP_SECRET"  # 飞书机器人的 Secret
CHAT_ID = "REDACTED_CHAT_ID_2" # 你的专属对话框 ID

def send_native_video(video_path):
    if not os.path.exists(video_path):
        print(f"找不到视频文件: {video_path}")
        return

    # 1. 获取飞书授权 Token
    print("正在获取授权 Token...")
    url_token = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res_token = requests.post(url_token, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    token = res_token.get("tenant_access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # 2. 【核心魔法】用 ffmpeg 自动抽取第一帧作为封面图
    print("正在抽取视频封面...")
    cover_path = video_path + "_cover.jpg"
    subprocess.run(["ffmpeg", "-i", video_path, "-vframes", "1", "-f", "image2", cover_path, "-y"], capture_output=True)

    # 3. 上传封面图，获取 image_key
    print("正在上传封面图...")
    url_img = "https://open.feishu.cn/open-apis/im/v1/images"
    with open(cover_path, 'rb') as f:
        res_img = requests.post(url_img, headers=headers, data={"image_type": "message"}, files={"image": f}).json()
    image_key = res_img.get("data", {}).get("image_key")

    # 用完就删掉临时封面
    if os.path.exists(cover_path):
        os.remove(cover_path)

    if not image_key:
        print("封面上传失败:", res_img)
        return
    print(f"封面上传成功: {image_key}")

    # 4. 上传视频本体，获取 file_key
    print("正在上传视频本体...")
    url_file = "https://open.feishu.cn/open-apis/im/v1/files"
    with open(video_path, 'rb') as f:
        res_file = requests.post(url_file, headers=headers, data={"file_type": "mp4", "file_name": os.path.basename(video_path)}, files={"file": f}).json()
    file_key = res_file.get("data", {}).get("file_key")

    if not file_key:
        print("视频上传失败:", res_file)
        return
    print(f"视频上传成功: {file_key}")

    # 5. 组合双 Key，发送原生 media 消息
    print("正在发送原生视频预览气泡...")
    url_send = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    payload = {
        "receive_id": CHAT_ID,
        "msg_type": "media",  # 【划重点】飞书的视频类型叫 media，不叫 video！
        "content": json.dumps({"file_key": file_key, "image_key": image_key})
    }
    res_send = requests.post(url_send, headers=headers, json=payload).json()
    print("任务完成！发送结果:", json.dumps(res_send, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("错误：请提供本地视频文件的路径。")
        sys.exit(1)
    send_native_video(sys.argv[1])
