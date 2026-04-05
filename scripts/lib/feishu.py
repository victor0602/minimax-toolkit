#!/usr/bin/env python3
# MIT License — Copyright (c) 2026 Victor
# https://github.com/victor0602/minimax-toolkit

"""
Feishu API 共享库
封装 token 获取、文件上传、消息发送等通用操作
"""
import os
import json
import requests


class FeishuAPI:
    """飞书 API 封装"""

    BASE_URL = "https://open.feishu.cn/open-apis"
    TOKEN_URL = f"{BASE_URL}/auth/v3/tenant_access_token/internal"

    def __init__(self, app_id=None, app_secret=None):
        self.app_id = app_id or os.environ.get("FEISHU_APP_ID", "")
        self.app_secret = app_secret or os.environ.get("FEISHU_APP_SECRET", "")
        self._token = None

    def check_config(self):
        """检查是否已配置"""
        if not self.app_id or not self.app_secret:
            print("[Error] FEISHU_APP_ID or FEISHU_APP_SECRET is not set.")
            print("  Set them in .env or export FEISHU_APP_ID / FEISHU_APP_SECRET")
            return False
        return True

    # ── Token ──────────────────────────────────────────────────────────────

    def get_token(self):
        """获取 tenant_access_token，失败返回 None"""
        if not self.app_id or not self.app_secret:
            return None
        res = requests.post(
            self.TOKEN_URL,
            json={"app_id": self.app_id, "app_secret": self.app_secret},
            timeout=10,
        ).json()
        token = res.get("tenant_access_token")
        if not token:
            print(f"[Error] Token failed: {res}")
        return token

    def headers(self, token=None):
        """返回带 Authorization 的请求头"""
        tok = token or self.get_token()
        if not tok:
            return None
        return {"Authorization": f"Bearer {tok}"}

    # ── Upload ────────────────────────────────────────────────────────────

    def upload_image(self, image_path, token=None):
        """
        上传图片，返回 image_key；失败返回 None
        POST /im/v1/images
        """
        hdrs = self.headers(token)
        if not hdrs:
            return None
        with open(image_path, "rb") as f:
            res = requests.post(
                f"{self.BASE_URL}/im/v1/images",
                headers=hdrs,
                data={"image_type": "message"},
                files={"Image": (os.path.basename(image_path), f, "image/jpeg")},
                timeout=30,
            ).json()
        image_key = res.get("data", {}).get("image_key")
        if not image_key:
            print(f"[Error] Image upload failed: {res}")
        return image_key

    def upload_file(self, file_path, file_type, token=None):
        """
        上传文件，返回 file_key；失败返回 None
        POST /im/v1/files
        file_type: stream | opus | mp4 | pdf | ...
        """
        hdrs = self.headers(token)
        if not hdrs:
            return None
        with open(file_path, "rb") as f:
            res = requests.post(
                f"{self.BASE_URL}/im/v1/files",
                headers=hdrs,
                data={"file_type": file_type, "file_name": os.path.basename(file_path)},
                files={"file": f},
                timeout=60,
            ).json()
        file_key = res.get("data", {}).get("file_key")
        if not file_key:
            print(f"[Error] File upload failed: {res}")
        return file_key

    # ── Send ─────────────────────────────────────────────────────────────

    def send(
        self,
        receive_id,
        msg_type,
        content,
        rid_type="chat_id",
        token=None,
    ):
        """
        发送消息，返回 API 响应 dict；失败返回 None
        receive_id: chat_id / open_id / user_id
        msg_type:   text | image | audio | file | media | post | sticker
        content:    JSON-serializable dict（内部会 json.dumps）
        rid_type:   chat_id | open_id | user_id
        """
        hdrs = self.headers(token)
        if not hdrs:
            return None
        res = requests.post(
            f"{self.BASE_URL}/im/v1/messages?receive_id_type={rid_type}",
            headers=hdrs,
            json={
                "receive_id": receive_id,
                "msg_type": msg_type,
                "content": json.dumps(content),
            },
            timeout=15,
        ).json()
        if res.get("code") != 0:
            print(f"[Error] Send failed: {res}")
            return None
        return res

    # ── Convenience ──────────────────────────────────────────────────────

    def send_text(self, receive_id, text, rid_type="chat_id", token=None):
        """发送文本消息"""
        return self.send(receive_id, "text", {"text": text}, rid_type, token)

    def send_image(self, receive_id, image_key, rid_type="chat_id", token=None):
        """发送图片消息"""
        return self.send(receive_id, "image", {"image_key": image_key}, rid_type, token)

    def send_audio(
        self, receive_id, file_key, rid_type="chat_id", token=None
    ):
        """发送原生语音（绿色气泡）"""
        return self.send(receive_id, "audio", {"file_key": file_key}, rid_type, token)

    def send_file(
        self, receive_id, file_key, rid_type="chat_id", token=None
    ):
        """发送文件消息（带播放器）"""
        return self.send(receive_id, "file", {"file_key": file_key}, rid_type, token)

    def send_media(
        self, receive_id, file_key, image_key, rid_type="chat_id", token=None
    ):
        """发送原生视频气泡（需封面图）"""
        return self.send(
            receive_id,
            "media",
            {"file_key": file_key, "image_key": image_key},
            rid_type,
            token,
        )

    # ── Chat management ───────────────────────────────────────────────────

    def list_chats(self, token=None):
        """
        获取机器人所在的所有群聊列表
        返回 list[dict]；失败返回 []
        GET /im/v1/chats
        """
        hdrs = self.headers(token)
        if not hdrs:
            return []
        chats = []
        page_token = None
        while True:
            params = {"page_size": 50}
            if page_token:
                params["page_token"] = page_token
            res = requests.get(
                f"{self.BASE_URL}/im/v1/chats",
                headers=hdrs, params=params, timeout=15,
            ).json()
            items = res.get("data", {}).get("items", [])
            chats.extend(items)
            page_token = res.get("data", {}).get("page_token")
            if not page_token or not res.get("data", {}).get("has_more", False):
                break
        return chats
