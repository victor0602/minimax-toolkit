#!/usr/bin/env python3
"""
MiniMax TTS wrapper
Usage: python3 tts.py tts "text" [-v voice] [-o output]
"""
import sys
import os
import json
import subprocess
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
WORKSPACE = PROJECT_ROOT  # Use toolkit root instead of hardcoded ~/.openclaw/workspace
SKILL_SCRIPT = os.path.join(SCRIPT_DIR, "tts", "generate_voice.sh")


def load_env():
    """Load .env file from project root or current directory."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    for env_file in [os.path.join(project_root, ".env"), os.path.join(os.getcwd(), ".env")]:
        if os.path.isfile(env_file):
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip()
                    if len(value) >= 2:
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                    if not os.environ.get(key):
                        os.environ[key] = value
            return


def tts(text, voice="female-shaonv", output="minimax-output/output.mp3", verbose=False):
    load_env()
    env = os.environ.copy()
    if not env.get("MINIMAX_API_KEY"):
        print("[Error] MINIMAX_API_KEY not set. Set it in environment or in your shell profile.", file=sys.stderr)
        return False

    env.setdefault("MINIMAX_API_HOST", "https://api.minimaxi.com")
    os.makedirs(os.path.dirname(os.path.abspath(output)) if os.path.dirname(output) else "minimax-output", exist_ok=True)

    if os.path.exists(SKILL_SCRIPT):
        result = subprocess.run(
            ["bash", SKILL_SCRIPT, "tts", text, "-v", voice, "-o", output],
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

    # Fallback: direct API call
    return tts_direct_api(text, voice, output, verbose)


def tts_direct_api(text, voice="female-shaonv", output="minimax-output/output.mp3", verbose=False):
    load_env()
    import requests

    api_key = os.environ.get("MINIMAX_API_KEY")
    api_host = os.environ.get("MINIMAX_API_HOST", "https://api.minimaxi.com")
    url = f"{api_host}/t2a_v2"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "speech-2.8-hd",
        "text": text,
        "voice_setting": {"voice_id": voice, "speed": 1.0, "vol": 1.0, "pitch": 0},
        "audio_setting": {"sample_rate": 32000, "bitrate": 128000, "format": "mp3", "channel": 1},
        "stream": False,
        "output_format": "hex",
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        base_resp = result.get("base_resp", {})
        if base_resp.get("status_code", 0) != 0:
            print(f"[Error] API Error: {base_resp.get('status_msg', 'Unknown')}", file=sys.stderr)
            return False

        audio_data = None
        if "data" in result and isinstance(result["data"], dict):
            audio_data = result["data"].get("audio")
        if not audio_data and "extra_info" in result:
            audio_data = result["extra_info"].get("audio")
        if not audio_data:
            audio_data = result.get("audio")

        if not audio_data:
            print(f"[Error] No audio data in response", file=sys.stderr)
            return False

        os.makedirs(os.path.dirname(os.path.abspath(output)) if os.path.dirname(output) else "minimax-output", exist_ok=True)
        audio_bytes = bytes.fromhex(audio_data)
        with open(output, "wb") as f:
            f.write(audio_bytes)
        print(f"[OK] 语音已生成: {output} ({len(audio_bytes)} bytes)")
        return True

    except Exception as e:
        print(f"[Error] {type(e).__name__}: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="MiniMax TTS 工具")
    sub = parser.add_subparsers(dest="command", help="命令")
    p_tts = sub.add_parser("tts", help="文字转语音")
    p_tts.add_argument("text", help="要转换的文本")
    p_tts.add_argument("-v", "--voice", default="female-shaonv", help="语音 ID")
    p_tts.add_argument("-o", "--output", default="minimax-output/output.mp3", help="输出文件路径")
    p_tts.add_argument("--verbose", action="store_true", help="显示调试信息")

    args = parser.parse_args()
    if args.command == "tts":
        success = tts(args.text, args.voice, args.output, args.verbose)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
