#!/usr/bin/env python3
import sys
import requests
import json
import os
import subprocess
import tempfile

# === 核心配置区 ===
APP_ID = "cli_a9140602d7389bca"
APP_SECRET = "ooqewzPrVtFpCWUDnWGnxfoKZ6dmIYVz"
CHAT_ID = "oc_c9183158e7521c3ead125cb26be15099"  # OpenClaw主控群

def convert_to_opus(input_path):
    """将音频转换为 .opus 格式"""
    temp_opus = tempfile.NamedTemporaryFile(delete=False, suffix='.opus')
    temp_opus.close()
    
    cmd = [
        'ffmpeg', '-i', input_path,
        '-c:a', 'libopus',
        '-b:a', '128k',
        '-y',  # 覆盖已存在的文件
        temp_opus.name
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"转换失败: {result.stderr}")
        return None
    return temp_opus.name

def send_audio_as_file(file_path):
    """发送音频文件（MP3/WAV等）- 飞书会渲染为音频播放器"""
    if not os.path.exists(file_path):
        print(f"找不到音频文件: {file_path}")
        return False

    # 1. 获取飞书授权 Token
    print("正在获取授权 Token...")
    url_token = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res_token = requests.post(url_token, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    token = res_token.get("tenant_access_token")
    if not token:
        print("Token 获取失败:", res_token)
        return False
    headers = {"Authorization": f"Bearer {token}"}

    # 2. 上传音频文件到飞书
    print("正在上传音频到飞书服务器...")
    url_upload = "https://open.feishu.cn/open-apis/im/v1/files"
    with open(file_path, 'rb') as f:
        data = {"file_type": "stream", "file_name": os.path.basename(file_path)}
        files = {"file": f}
        res_upload = requests.post(url_upload, headers=headers, data=data, files=files).json()

    file_key = res_upload.get("data", {}).get("file_key")
    if not file_key:
        print("音频上传失败:", res_upload)
        return False

    # 3. 发送音频消息
    print("正在发送音频消息...")
    url_send = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    payload = {
        "receive_id": CHAT_ID,
        "msg_type": "file",
        "content": json.dumps({"file_key": file_key})
    }
    res_send = requests.post(url_send, headers=headers, json=payload).json()
    print("发送成功！")
    return True

def send_audio_as_voice(file_path):
    """发送原生语音消息（.opus格式）- 绿色气泡"""
    if not os.path.exists(file_path):
        print(f"找不到音频文件: {file_path}")
        return False

    # 转换为 opus
    print("正在转换为 .opus 格式...")
    opus_path = convert_to_opus(file_path)
    if not opus_path:
        return False
    
    print(f"转换完成: {opus_path}")

    # 1. 获取飞书授权 Token
    print("正在获取授权 Token...")
    url_token = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res_token = requests.post(url_token, json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()
    token = res_token.get("tenant_access_token")
    if not token:
        print("Token 获取失败:", res_token)
        os.unlink(opus_path)
        return False
    headers = {"Authorization": f"Bearer {token}"}

    # 2. 上传 opus 文件
    print("正在上传到飞书服务器...")
    url_upload = "https://open.feishu.cn/open-apis/im/v1/files"
    with open(opus_path, 'rb') as f:
        data = {"file_type": "opus", "file_name": os.path.basename(opus_path)}
        files = {"file": f}
        res_upload = requests.post(url_upload, headers=headers, data=data, files=files).json()
    
    os.unlink(opus_path)  # 删除临时文件

    file_key = res_upload.get("data", {}).get("file_key")
    if not file_key:
        print("上传失败:", res_upload)
        return False

    # 3. 发送原生语音消息
    print("正在发送原生语音...")
    url_send = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    payload = {
        "receive_id": CHAT_ID,
        "msg_type": "audio",
        "content": json.dumps({"file_key": file_key})
    }
    res_send = requests.post(url_send, headers=headers, json=payload).json()
    print("发送成功！")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("错误：请提供音频文件路径。")
        print("用法:")
        print("  python3 send_feishu_audio.py <文件路径>           # 发送原生语音（绿色气泡）")
        print("  python3 send_feishu_audio.py <文件路径> file      # 发送音频文件（播放器形式）")
        sys.exit(1)
    
    file_path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "opus"  # 默认使用原生语音（绿色气泡）
    
    if mode == "opus":
        success = send_audio_as_voice(file_path)
    else:
        success = send_audio_as_file(file_path)
    
    sys.exit(0 if success else 1)
