#!/usr/bin/env python3
"""
Feature integration tests for MiniMax Toolkit.
Run: python3 scripts/test_features.py
Requires: MINIMAX_API_KEY environment variable or .env file
"""
import sys
import os
import json
import tempfile
import subprocess
import requests
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent

PASS = "\033[0;32m✓\033[0m"
FAIL = "\033[0;31m✗\033[0m"
SKIP = "\033[0;33m⊘\033[0m"


def get_api_key():
    """Get API key from env or .env file."""
    # Try environment first
    key = os.environ.get("MINIMAX_API_KEY", "")
    if key:
        return key
    # Try .env file
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("MINIMAX_API_KEY=") and "=" in line:
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                if key:
                    return key
    return ""


def check_api_key():
    """Check if API key is available."""
    key = get_api_key()
    if not key or key in ("sk-cp-xxx", "sk-api-xxx", "YOUR_API_KEY"):
        return None
    return key


def test_api_connectivity():
    """Test API connectivity."""
    print("\n[Test] API Connectivity")
    api_key = check_api_key()
    if not api_key:
        print(f"  {SKIP} No API key, skipping")
        return None

    host = os.environ.get("MINIMAX_API_HOST", "https://api.minimaxi.com")
    try:
        resp = requests.post(
            f"{host}/v1/t2a_v2",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "speech-2.8-hd",
                "text": "test",
                "voice_setting": {"voice_id": "female-shaonv", "speed": 1.0},
                "audio_setting": {"sample_rate": 32000, "bitrate": 128000, "format": "mp3", "channel": 1}
            },
            timeout=30
        )
        if resp.status_code < 400:
            print(f"  {PASS} API reachable (status: {resp.status_code})")
            return True
        else:
            err = resp.json().get("base_resp", {}).get("status_msg", f"HTTP {resp.status_code}")
            print(f"  {FAIL} API error: {err}")
            return False
    except Exception as e:
        print(f"  {FAIL} Connection failed: {str(e)[:100]}")
        return False


def test_tts():
    """Test TTS generation."""
    print("\n[Test] TTS Generation")
    api_key = check_api_key()
    if not api_key:
        print(f"  {SKIP} No API key, skipping")
        return None

    host = os.environ.get("MINIMAX_API_HOST", "https://api.minimaxi.com")
    try:
        resp = requests.post(
            f"{host}/v1/t2a_v2",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "speech-2.8-hd",
                "text": "hello test",
                "voice_setting": {"voice_id": "female-shaonv", "speed": 1.0, "vol": 1.0, "pitch": 0},
                "audio_setting": {"sample_rate": 32000, "bitrate": 128000, "format": "mp3", "channel": 1},
                "stream": False,
                "output_format": "hex"
            },
            timeout=30
        )
        data = resp.json()
        if resp.status_code < 400 and data.get("data", {}).get("audio"):
            audio_hex = data["data"]["audio"]
            print(f"  {PASS} TTS generated (hex length: {len(audio_hex)})")
            return True
        else:
            err = data.get("base_resp", {}).get("status_msg", f"HTTP {resp.status_code}")
            print(f"  {FAIL} TTS failed: {err}")
            return False
    except Exception as e:
        print(f"  {FAIL} TTS exception: {str(e)[:100]}")
        return False


def test_image_generation():
    """Test image generation."""
    print("\n[Test] Image Generation")
    api_key = check_api_key()
    if not api_key:
        print(f"  {SKIP} No API key, skipping")
        return None

    host = os.environ.get("MINIMAX_API_HOST", "https://api.minimaxi.com")
    try:
        resp = requests.post(
            f"{host}/v1/image_generation",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "image-01",
                "prompt": "a simple red circle",
                "response_format": "url",
                "n": 1
            },
            timeout=30
        )
        data = resp.json()
        if resp.status_code < 400:
            urls = data.get("data", {}).get("image_urls", [])
            if urls:
                print(f"  {PASS} Image generated: {urls[0][:50]}...")
                return True
        err = data.get("base_resp", {}).get("status_msg", f"HTTP {resp.status_code}")
        print(f"  {FAIL} Image generation failed: {err}")
        return False
    except Exception as e:
        print(f"  {FAIL} Image exception: {str(e)[:100]}")
        return False


def test_music_generation():
    """Test music generation."""
    print("\n[Test] Music Generation")
    api_key = check_api_key()
    if not api_key:
        print(f"  {SKIP} No API key, skipping")
        return None

    host = os.environ.get("MINIMAX_API_HOST", "https://api.minimaxi.com")
    try:
        resp = requests.post(
            f"{host}/v1/music_generation",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "music-2.5",
                "prompt": "short instrumental test",
                "lyrics": "[verse] test [chorus] test",
                "output_format": "url",
                "stream": False
            },
            timeout=60
        )
        data = resp.json() or {}
        if resp.status_code < 400:
            # Try different response structures
            audio_url = (data.get("data") or {}).get("audio_url")
            if not audio_url:
                audio_url = (data.get("data") or {}).get("audio")
            if audio_url:
                print(f"  {PASS} Music generated: {str(audio_url)[:50]}...")
                return True
        err = (data.get("base_resp") or {}).get("status_msg") or f"HTTP {resp.status_code}"
        print(f"  {FAIL} Music generation failed: {err}")
        return False
    except Exception as e:
        print(f"  {FAIL} Music exception: {str(e)[:100]}")
        return False


def test_video_generation():
    """Test video generation."""
    print("\n[Test] Video Generation")
    api_key = check_api_key()
    if not api_key:
        print(f"  {SKIP} No API key, skipping")
        return None

    host = os.environ.get("MINIMAX_API_HOST", "https://api.minimaxi.com")
    try:
        resp = requests.post(
            f"{host}/v1/video_generation",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "MiniMax-Hailuo-2.3",
                "prompt": "test video",
                "duration": 6,
                "resolution": "768P"
            },
            timeout=30
        )
        data = resp.json()
        if resp.status_code < 400:
            task_id = data.get("task_id")
            if task_id:
                print(f"  {PASS} Video task created: {task_id}")
                return True
        err = data.get("base_resp", {}).get("status_msg", f"HTTP {resp.status_code}")
        print(f"  {FAIL} Video generation failed: {err}")
        return False
    except Exception as e:
        print(f"  {FAIL} Video exception: {str(e)[:100]}")
        return False


def test_toolkit_cli():
    """Test toolkit CLI commands work."""
    print("\n[Test] Toolkit CLI Commands")
    api_key = check_api_key()
    project_root = SCRIPT_DIR.parent
    toolkit_py = project_root / "scripts/toolkit.py"

    tests = [
        ("doctor", ["doctor"]),
    ]
    if api_key:
        tests.append(("env --show", ["env", "--show"]))

    all_ok = True
    for name, args in tests:
        result = subprocess.run(
            ["python3", str(toolkit_py)] + args,
            capture_output=True, text=True, cwd=str(project_root),
            env={**os.environ, "MINIMAX_API_KEY": api_key or "sk-cp-test"}
        )
        if result.returncode == 0:
            print(f"  {PASS} toolkit.py {' '.join(args)}")
        else:
            print(f"  {FAIL} toolkit.py {' '.join(args)} (exit: {result.returncode})")
            all_ok = False
    return all_ok


def test_feishu_config():
    """Test Feishu configuration if provided."""
    print("\n[Test] Feishu Configuration")
    app_id = os.environ.get("FEISHU_APP_ID", "")
    app_secret = os.environ.get("FEISHU_APP_SECRET", "")

    if not app_id or not app_secret:
        print(f"  {SKIP} Feishu not configured, skipping")
        return None

    try:
        resp = requests.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": app_id, "app_secret": app_secret},
            timeout=10
        )
        data = resp.json()
        if resp.status_code < 400 and data.get("tenant_access_token"):
            print(f"  {PASS} Feishu token obtained")
            # Test listing chats
            token = data["tenant_access_token"]
            chats_resp = requests.get(
                "https://open.feishu.cn/open-apis/im/v1/chats",
                headers={"Authorization": f"Bearer {token}"},
                params={"page_size": 5},
                timeout=10
            )
            if chats_resp.status_code < 400:
                count = len(chats_resp.json().get("data", {}).get("items", []))
                print(f"  {PASS} Feishu chat list accessible ({count} visible)")
                return True
            print(f"  {WARN} Feishu chat list not accessible")
            return False
        print(f"  {FAIL} Feishu auth failed")
        return False
    except Exception as e:
        print(f"  {FAIL} Feishu exception: {str(e)[:100]}")
        return False


def main():
    print("=" * 50)
    print("MiniMax Toolkit — Feature Tests")
    print("=" * 50)

    api_key = check_api_key()
    if not api_key:
        print(f"\n{WARN} No API key found. Feature tests will be skipped.")
        print(f"    Set MINIMAX_API_KEY or run: python3 scripts/toolkit.py setup")
    else:
        masked = api_key[:8] + "..."
        print(f"\nUsing API key: {masked}")

    results = []

    results.append(("API Connectivity", test_api_connectivity()))
    results.append(("TTS Generation", test_tts()))
    results.append(("Image Generation", test_image_generation()))
    results.append(("Music Generation", test_music_generation()))
    results.append(("Video Generation", test_video_generation()))
    results.append(("Toolkit CLI", test_toolkit_cli()))
    results.append(("Feishu Config", test_feishu_config()))

    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)

    passed = 0
    failed = 0
    skipped = 0

    for name, result in results:
        if result is None:
            status = f"{SKIP} SKIP"
            skipped += 1
        elif result:
            status = f"{PASS} PASS"
            passed += 1
        else:
            status = f"{FAIL} FAIL"
            failed += 1
        print(f"  {status}  {name}")

    print()
    total = passed + failed + skipped
    print(f"Results: {passed}/{total} passed, {failed} failed, {skipped} skipped")

    if failed > 0:
        print(f"\n{FAIL} Some feature tests failed.")
        return 1
    elif skipped > 0 and passed == 0:
        print(f"\n{SKIP} No feature tests ran (no API key).")
        return 2
    else:
        print(f"\n{PASS} All feature tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
