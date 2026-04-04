#!/usr/bin/env python3
"""
发送原生视频气泡到飞书（封面图 + mp4 分别上传）
  python3 send_feishu_native_video.py <video_file>
"""
import sys
import os
import subprocess
import scripts.lib.feishu as feishu

CHAT_ID = os.environ.get("FEISHU_CHAT_ID", "")


def extract_cover(video_path):
    """用 ffmpeg 抽取第一帧作为封面，返回临时 jpg 路径；失败返回 None"""
    cover_path = video_path + "_cover.jpg"
    r = subprocess.run(
        ["ffmpeg", "-i", video_path, "-vframes", "1", "-f", "image2", cover_path, "-y"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"[Error] 封面倒抽取失败: {r.stderr}")
        return None
    return cover_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 send_feishu_native_video.py <video_file>")
        sys.exit(1)

    video_path = sys.argv[1]
    if not os.path.exists(video_path):
        print(f"[Error] 文件不存在: {video_path}")
        sys.exit(1)

    receive_id = os.environ.get("FEISHU_CHAT_ID", "")
    if not receive_id:
        print("[Error] FEISHU_CHAT_ID is not set.")
        sys.exit(1)

    api = feishu.FeishuAPI()
    if not api.check_config():
        sys.exit(1)

    # 1. 抽取封面
    print("[Info] 正在抽取视频封面...")
    cover_path = extract_cover(video_path)
    if not cover_path:
        sys.exit(1)

    # 2. 上传封面
    print("[Info] 正在上传封面...")
    image_key = api.upload_image(cover_path)
    os.unlink(cover_path)
    if not image_key:
        sys.exit(1)
    print(f"[Info] 封面上传成功: {image_key}")

    # 3. 上传视频
    print("[Info] 正在上传视频...")
    file_key = api.upload_file(video_path, "mp4")
    if not file_key:
        sys.exit(1)
    print(f"[Info] 视频上传成功: {file_key}")

    # 4. 发送原生视频气泡
    print("[Info] 正在发送视频气泡...")
    res = api.send_media(receive_id, file_key, image_key)
    if not res:
        sys.exit(1)

    print("[OK] 原生视频气泡发送成功")
    sys.exit(0)
