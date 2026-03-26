#!/usr/bin/env python3
"""
MiniMax TTS wrapper - 优化版
支持直接调用 API，兼容语音合成功能

Usage: python3 tts.py tts "text" [-v voice] [-o output]
       python3 tts.py api "text" [-v voice]  # 直接调用 API 返回 JSON
"""
import sys
import os
import json
import subprocess
import argparse

USER_HOME = os.path.expanduser("~")
WORKSPACE = os.path.join(USER_HOME, ".openclaw/workspace")
SKILL_MULTIMODAL = os.path.join(USER_HOME, ".openclaw/workspace/skills/minimax-multimodal")


def tts(text, voice="female-shaonv", output="minimax-output/output.mp3", verbose=False):
    """
    使用 MiniMax API 生成语音

    Args:
        text: 要转换的文本
        voice: 语音 ID
        output: 输出文件路径
        verbose: 是否输出详细信息

    Returns:
        bool: 是否成功
    """
    env = os.environ.copy()
    if not env.get("MINIMAX_API_KEY"):
        print("[Error] MINIMAX_API_KEY not set. Set it in environment or in your shell profile.", file=sys.stderr)
        return False

    env.setdefault("MINIMAX_API_HOST", "https://api.minimaxi.com")

    # 确保输出目录存在
    os.makedirs(os.path.dirname(os.path.abspath(output)) if os.path.dirname(output) else "minimax-output", exist_ok=True)

    # 使用 minimax-multimodal 的脚本
    script_path = f"{SKILL_MULTIMODAL}/scripts/tts/generate_voice.py"

    if not os.path.exists(script_path):
        # 如果找不到脚本，直接调用 API
        return tts_direct_api(text, voice, output, verbose)

    result = subprocess.run(
        ["python3", script_path, "tts", text, "-v", voice, "-o", output],
        cwd=WORKSPACE,
        env=env,
        capture_output=True,
        text=True
    )

    if verbose or result.returncode != 0:
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

    if result.returncode == 0 and os.path.exists(output):
        print(f"[OK] 语音已生成: {output}")
        return True
    else:
        # 尝试直接 API 调用作为后备
        print("[Info] minimax-multimodal 脚本失败，尝试直接 API 调用...", file=sys.stderr)
        return tts_direct_api(text, voice, output, verbose)


def tts_direct_api(text, voice="female-shaonv", output="minimax-output/output.mp3", verbose=False):
    """
    直接调用 MiniMax TTS API，不依赖外部脚本
    """
    import requests

    api_key = os.environ.get("MINIMAX_API_KEY")
    api_host = os.environ.get("MINIMAX_API_HOST", "https://api.minimaxi.com")

    url = f"{api_host}/t2a_v2"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "speech-2.8-hd",
        "text": text,
        "voice_setting": {
            "voice_id": voice,
            "speed": 1.0,
            "vol": 1.0,
            "pitch": 0,
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1,
        },
        "stream": False,
        "output_format": "hex",
    }

    if verbose:
        print(f"[Debug] Calling API: {url}")
        print(f"[Debug] Voice: {voice}")
        print(f"[Debug] Text length: {len(text)} chars")

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        result = response.json()

        if verbose:
            print(f"[Debug] Response keys: {list(result.keys())}")

        # 检查 API 错误
        base_resp = result.get("base_resp", {})
        status_code = base_resp.get("status_code", 0)

        if status_code != 0:
            status_msg = base_resp.get("status_msg", "Unknown error")
            print(f"[Error] API Error [{status_code}]: {status_msg}", file=sys.stderr)
            return False

        # 提取音频数据 - 多种可能的位置
        audio_data = None

        # 方式1: data.audio
        if "data" in result and isinstance(result["data"], dict):
            audio_data = result["data"].get("audio")

        # 方式2: extra_info.audio
        if not audio_data and "extra_info" in result and isinstance(result["extra_info"], dict):
            audio_data = result["extra_info"].get("audio")

        # 方式3: 直接在根目录
        if not audio_data:
            audio_data = result.get("audio")

        if not audio_data:
            print(f"[Error] No audio data in response. Keys: {list(result.keys())}", file=sys.stderr)
            if verbose:
                print(f"[Debug] Full response: {json.dumps(result, ensure_ascii=False)[:500]}")
            return False

        # 保存音频文件
        os.makedirs(os.path.dirname(os.path.abspath(output)) if os.path.dirname(output) else "minimax-output", exist_ok=True)
        audio_bytes = bytes.fromhex(audio_data)

        with open(output, "wb") as f:
            f.write(audio_bytes)

        print(f"[OK] 语音已生成: {output} ({len(audio_bytes)} bytes)")
        return True

    except requests.exceptions.Timeout:
        print(f"[Error] API 请求超时（120秒）", file=sys.stderr)
        return False
    except requests.exceptions.RequestException as e:
        print(f"[Error] HTTP 请求失败: {e}", file=sys.stderr)
        return False
    except json.JSONDecodeError as e:
        print(f"[Error] 响应 JSON 解析失败: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[Error] {type(e).__name__}: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="MiniMax TTS 工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 tts.py tts "你好，世界" -v female-shaonv -o output.mp3
  python3 tts.py tts "Hello world" -v male-qn-qingse -o hello.mp3 --verbose
  python3 tts.py api "测试" -v female-shaonv  # 直接返回 API JSON
        """
    )

    sub = parser.add_subparsers(dest="command", help="命令")

    # tts 命令
    p_tts = sub.add_parser("tts", help="文字转语音")
    p_tts.add_argument("text", help="要转换的文本")
    p_tts.add_argument("-v", "--voice", default="female-shaonv", help="语音 ID (默认: female-shaonv)")
    p_tts.add_argument("-o", "--output", default="minimax-output/output.mp3", help="输出文件路径")
    p_tts.add_argument("--verbose", action="store_true", help="显示调试信息")

    # api 命令 - 直接返回 JSON
    p_api = sub.add_parser("api", help="直接调用 API 返回 JSON")
    p_api.add_argument("text", help="要转换的文本")
    p_api.add_argument("-v", "--voice", default="female-shaonv", help="语音 ID")

    args = parser.parse_args()

    if args.command == "tts":
        success = tts(args.text, args.voice, args.output, args.verbose)
        sys.exit(0 if success else 1)
    elif args.command == "api":
        # 直接打印 JSON 响应
        import requests
        api_key = os.environ.get("MINIMAX_API_KEY")
        api_host = os.environ.get("MINIMAX_API_HOST", "https://api.minimaxi.com")

        if not api_key:
            print("[Error] MINIMAX_API_KEY not set", file=sys.stderr)
            sys.exit(1)

        url = f"{api_host}/t2a_v2"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "speech-2.8-hd",
            "text": args.text,
            "voice_setting": {
                "voice_id": args.voice,
                "speed": 1.0,
                "vol": 1.0,
                "pitch": 0,
            },
            "audio_setting": {
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": "mp3",
                "channel": 1,
            },
            "stream": False,
            "output_format": "hex",
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            print(json.dumps(response.json(), ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"[Error] {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
