#!/usr/bin/env python3
"""
MiniMax Toolkit — Unified CLI for all MiniMax capabilities.

Usage:
    python3 scripts/toolkit.py <command> [options]

Commands:
    setup       First-run setup wizard (interactive)
    check       Run diagnostic checks (use --json for machine output)
    env         Show or set environment variables
    tts         Text-to-speech
    image       Image generation
    music       Music generation
    video       Video generation
    feishu      Feishu group chat management and sending

Examples:
    python3 scripts/toolkit.py check --json          # Agent: get all status
    python3 scripts/toolkit.py setup                  # First-run setup
    python3 scripts/toolkit.py tts "hello world"     # Quick TTS
    python3 scripts/toolkit.py image "a cat"         # Quick image
    python3 scripts/toolkit.py env --show           # Show current config
    python3 scripts/toolkit.py feishu list          # List all bot groups
    python3 scripts/toolkit.py feishu send <file>   # Send file to selected group
"""
import sys
import os
import json
import subprocess
import argparse
import shlex
import requests
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
WORKSPACE = PROJECT_ROOT  # Use toolkit root instead of hardcoded ~/.openclaw/workspace

VERSION = "1.4.0"

# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class ToolError(Exception):
    """Structured error with code, message, hint."""
    def __init__(self, code, message, hint=None, file=None):
        self.code = code
        self.message = message
        self.hint = hint
        self.file = file
        super().__init__(message)

    def to_json(self):
        return json.dumps({
            "error": {
                "code": self.code,
                "message": self.message,
                **({"hint": self.hint} if self.hint else {}),
                **({"file": self.file} if self.file else {}),
            }
        })

    def print_json(self, file=None):
        print(self.to_json(), file=file or sys.stderr)


def error_exit(code, message, hint=None):
    e = ToolError(code, message, hint=hint)
    e.print_json()
    sys.exit(1)


def load_env():
    """Load .env from project root or cwd."""
    for env_file in [PROJECT_ROOT / ".env", Path.cwd() / ".env"]:
        if env_file.is_file():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip()
                    if len(value) >= 2 and (
                        (value.startswith('"') and value.endswith('"')) or
                        (value.startswith("'") and value.endswith("'"))
                    ):
                        value = value[1:-1]
                    if not os.environ.get(key):
                        os.environ[key] = value
            return


def require_api_key():
    load_env()
    if not os.environ.get("MINIMAX_API_KEY"):
        error_exit(
            "E_API_KEY_MISSING",
            "MINIMAX_API_KEY is not set",
            hint="Run: python3 scripts/toolkit.py env --key <your-api-key>"
        )


def run_bash(script_path, *args, capture=True, check=True, timeout=300):
    """Run a bash script with given args, inheriting env."""
    cmd = ["bash", str(script_path)] + list(args)
    env = os.environ.copy()
    env.setdefault("MINIMAX_API_HOST", "https://api.minimaxi.com")
    result = subprocess.run(
        cmd,
        cwd=str(WORKSPACE),
        env=env,
        capture_output=capture,
        text=True,
        timeout=timeout,
        check=False,
    )
    if capture:
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        hint = None
        if "MINIMAX_API_KEY" in result.stderr:
            hint = "Run: python3 scripts/toolkit.py env --key <your-api-key>"
        error_exit(
            "E_SCRIPT_FAILED",
            f"Script {script_path.name} failed with exit code {result.returncode}",
            hint=hint,
        )
    return result


def run_python(script_path, *args, check=True):
    """Run a python script as subprocess."""
    cmd = ["python3", str(script_path)] + list(args)
    env = os.environ.copy()
    result = subprocess.run(
        cmd,
        cwd=str(WORKSPACE),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        error_exit(
            "E_SCRIPT_FAILED",
            f"Script {script_path.name} failed",
        )
    return result


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_setup(args):
    script = SCRIPT_DIR / "setup.sh"
    result = subprocess.run(
        ["bash", str(script)] + (["--non-interactive"] if args.non_interactive else []),
        cwd=str(PROJECT_ROOT),
        env=os.environ.copy(),
    )
    sys.exit(result.returncode)


def cmd_check(args):
    script = SCRIPT_DIR / "check.sh"
    cmd = ["bash", str(script)]
    if args.json:
        cmd.append("--json")
    if args.feature:
        cmd.extend(["--feature", args.feature])

    env = os.environ.copy()
    env.setdefault("MINIMAX_API_HOST", "https://api.minimaxi.com")

    result = subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    if args.json:
        # Only output JSON lines to stdout (diagnose.sh already uses stderr for progress)
        # The check.sh sends diagnostic output to stderr, but in --json mode we want
        # the JSON to stdout. diagnose.sh outputs JSON to stdout already.
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    else:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)


def cmd_env(args):
    load_env()
    if args.show:
        key = os.environ.get("MINIMAX_API_KEY", "")
        host = os.environ.get("MINIMAX_API_HOST", "https://api.minimaxi.com")
        masked = key[:8] + "..." if key else "(not set)"
        key_type = "unknown"
        if key.startswith("sk-cp-"):
            key_type = "Token Plan (sk-cp-)"
        elif key.startswith("sk-api-"):
            key_type = "API Key (sk-api-)"
        print(f"MINIMAX_API_KEY : {masked} [{key_type}]")
        print(f"MINIMAX_API_HOST : {host}")
        print(f"Config file      : {PROJECT_ROOT / '.env'}")
        return

    if args.key:
        env_file = PROJECT_ROOT / ".env"
        content = f"""# MiniMax API 配置

# API Key（sk-cp- 开头为 Token Plan Key，sk-api- 开头为 API Key）
MINIMAX_API_KEY={args.key}

# API 地址（默认中国大陆）
MINIMAX_API_HOST=https://api.minimaxi.com
"""
        with open(env_file, "w") as f:
            f.write(content)
        print(f"API key saved to {env_file}")
        print(f"Run 'python3 scripts/toolkit.py check --json' to verify.")
        return

    # No args — show help
    print(__doc__)


def cmd_tts(args):
    require_api_key()
    output = args.output or str(PROJECT_ROOT / "minimax-output" / "output.mp3")
    os.makedirs(os.path.dirname(os.path.abspath(output)) if os.path.dirname(output) else "minimax-output", exist_ok=True)
    run_bash(
        SCRIPT_DIR / "tts.py",
        "tts", args.text,
        "-v", args.voice,
        "-o", output,
        check=True,
    )


def cmd_image(args):
    require_api_key()
    output = args.output or str(PROJECT_ROOT / "minimax-output" / "image.png")
    os.makedirs(os.path.dirname(os.path.abspath(output)) if os.path.dirname(output) else "minimax-output", exist_ok=True)
    cmd = [
        str(SCRIPT_DIR / "image_generate.py"),
        args.prompt,
        "-o", output,
    ]
    if args.download:
        cmd.append("--download")
    if args.aspect_ratio:
        cmd.extend(["--aspect-ratio", args.aspect_ratio])
    if args.mode:
        cmd.extend(["--mode", args.mode])

    result = subprocess.run(
        ["python3"] + cmd,
        cwd=str(WORKSPACE),
        env=os.environ.copy(),
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        error_exit("E_IMAGE_FAILED", "Image generation failed")
    sys.exit(0)


def cmd_music(args):
    require_api_key()
    output = args.output or str(PROJECT_ROOT / "minimax-output" / "music.mp3")
    os.makedirs(os.path.dirname(os.path.abspath(output)) if os.path.dirname(output) else "minimax-output", exist_ok=True)
    cmd = [
        "bash", str(SCRIPT_DIR / "music" / "generate_music.sh"),
        "--prompt", args.prompt,
        "-o", output,
        "--download",
    ]
    if args.lyrics:
        cmd.extend(["--lyrics", args.lyrics])
    if args.instrumental:
        cmd.append("--instrumental")

    result = subprocess.run(
        cmd,
        cwd=str(WORKSPACE),
        env=os.environ.copy(),
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        error_exit("E_MUSIC_FAILED", "Music generation failed")
    sys.exit(0)


def cmd_video(args):
    require_api_key()
    output = args.output or str(PROJECT_ROOT / "minimax-output" / "video.mp4")
    os.makedirs(os.path.dirname(os.path.abspath(output)) if os.path.dirname(output) else "minimax-output", exist_ok=True)
    cmd = [
        "bash", str(SCRIPT_DIR / "video" / "generate_video.sh"),
        "--mode", args.mode or "t2v",
        "--prompt", args.prompt,
        "-o", output,
    ]
    if args.duration:
        cmd.extend(["--duration", str(args.duration)])
    if args.first_frame:
        cmd.extend(["--first-frame", args.first_frame])

    result = subprocess.run(
        cmd,
        cwd=str(WORKSPACE),
        env=os.environ.copy(),
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        error_exit("E_VIDEO_FAILED", "Video generation failed")
    sys.exit(0)


# ---------------------------------------------------------------------------
# Feishu helpers
# ---------------------------------------------------------------------------

def get_feishu_token():
    """Get Feishu tenant access token."""
    app_id = os.environ.get("FEISHU_APP_ID", "")
    app_secret = os.environ.get("FEISHU_APP_SECRET", "")
    if not app_id or not app_secret:
        error_exit("E_FEISHU_NOT_CONFIGURED", "FEISHU_APP_ID and FEISHU_APP_SECRET are not set")
    res = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret}
    ).json()
    token = res.get("tenant_access_token")
    if not token:
        error_exit("E_FEISHU_TOKEN_FAILED", f"Failed to get token: {res}")
    return token


def list_feishu_chats(token):
    """List all chats the bot is in."""
    headers = {"Authorization": f"Bearer {token}"}
    chats = []
    page_token = None
    while True:
        params = {"page_size": 50}
        if page_token:
            params["page_token"] = page_token
        res = requests.get(
            "https://open.feishu.cn/open-apis/im/v1/chats",
            headers=headers, params=params
        ).json()
        items = res.get("data", {}).get("items", [])
        chats.extend(items)
        page_token = res.get("data", {}).get("page_token")
        if not page_token or not res.get("data", {}).get("has_more", False):
            break
    return chats


def select_chat_interactive(chats):
    """Let user select a chat interactively."""
    if not chats:
        print("No chats found.")
        return None
    print(f"\n{'='*50}")
    print(f"Found {len(chats)} chats:")
    print(f"{'='*50}")
    for i, chat in enumerate(chats, 1):
        name = chat.get("name", "Unnamed")
        member_count = chat.get("member_count", 0)
        print(f"  [{i}] {name} (members: {member_count})")
    print(f"{'='*50}")
    print("  [0] Cancel")
    while True:
        try:
            choice = input("\nEnter chat number: ").strip()
            idx = int(choice)
            if idx == 0:
                return None
            if 1 <= idx <= len(chats):
                return chats[idx - 1]
            print("Invalid number")
        except ValueError:
            print("Please enter a number")


def send_image_to_chat(token, file_path, chat_id):
    """Upload and send image to chat."""
    headers = {"Authorization": f"Bearer {token}"}
    with open(file_path, "rb") as f:
        files = {"image": (os.path.basename(file_path), f, "image/jpeg")}
        data = {"image_type": "message"}
        res = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/images",
            headers=headers, data=data, files=files
        ).json()
    image_key = res.get("data", {}).get("image_key")
    if not image_key:
        return False, f"Upload failed: {res}"
    payload = {
        "receive_id": chat_id,
        "msg_type": "image",
        "content": json.dumps({"image_key": image_key})
    }
    res = requests.post(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        headers=headers, json=payload
    ).json()
    if res.get("code") == 0:
        return True, "Sent successfully"
    return False, f"Send failed: {res}"


def send_file_to_chat(token, file_path, chat_id):
    """Upload and send file to chat."""
    headers = {"Authorization": f"Bearer {token}"}
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "application/octet-stream")}
        data = {
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path)
        }
        res = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/files",
            headers=headers, data=data, files=files
        ).json()
    file_key = res.get("data", {}).get("file_key")
    if not file_key:
        return False, f"Upload failed: {res}"
    payload = {
        "receive_id": chat_id,
        "msg_type": "file",
        "content": json.dumps({"file_key": file_key})
    }
    res = requests.post(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        headers=headers, json=payload
    ).json()
    if res.get("code") == 0:
        return True, "Sent successfully"
    return False, f"Send failed: {res}"


def get_file_type(file_path):
    """Return file category based on extension."""
    ext = os.path.splitext(file_path)[1].lower()
    image_exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    audio_exts = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".wma"}
    video_exts = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"}
    if ext in image_exts:
        return "image"
    elif ext in audio_exts:
        return "audio"
    elif ext in video_exts:
        return "video"
    return "file"


# ---------------------------------------------------------------------------
# Feishu command
# ---------------------------------------------------------------------------

def cmd_feishu(args):
    if args.feishu_sub == "list":
        token = get_feishu_token()
        chats = list_feishu_chats(token)
        for chat in chats:
            name = chat.get("name", "Unnamed")
            chat_id = chat.get("chat_id", "")
            member_count = chat.get("member_count", 0)
            print(f"  {name} | {chat_id} | {member_count} members")
        return

    elif args.feishu_sub == "send":
        if not args.file:
            error_exit("E_MISSING_ARG", "File path is required for send command")
        if not os.path.exists(args.file):
            error_exit("E_FILE_NOT_FOUND", f"File not found: {args.file}")

        token = get_feishu_token()
        chats = list_feishu_chats(token)
        chat = select_chat_interactive(chats)
        if not chat:
            print("Cancelled")
            return

        chat_id = chat.get("chat_id")
        chat_name = chat.get("name")
        file_type = get_file_type(args.file)

        if file_type == "image":
            success, msg = send_image_to_chat(token, args.file, chat_id)
        else:
            success, msg = send_file_to_chat(token, args.file, chat_id)

        print(f"\n[{chat_name}] {msg}")
        return

    else:
        error_exit("E_UNKNOWN_SUBCOMMAND", f"Unknown feishu subcommand: {args.feishu_sub}")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        description="MiniMax Toolkit — Unified CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", help="Commands")

    # setup
    p_setup = sub.add_parser("setup", help="First-run setup wizard")

    # check
    p_check = sub.add_parser("check", help="Run diagnostic checks")
    p_check.add_argument("--json", action="store_true", help="JSON output (for agents)")
    p_check.add_argument("--feature", choices=["tts","image","music","video","mcporter","env","api_key","dependencies"], help="Check specific feature only")

    # env
    p_env = sub.add_parser("env", help="Show or set environment variables")
    p_env.add_argument("--show", action="store_true", help="Show current environment")
    p_env.add_argument("--key", help="Set MINIMAX_API_KEY")

    # tts
    p_tts = sub.add_parser("tts", help="Text-to-speech")
    p_tts.add_argument("text", help="Text to synthesize")
    p_tts.add_argument("-v", "--voice", default="female-shaonv", help="Voice ID (default: female-shaonv)")
    p_tts.add_argument("-o", "--output", help="Output file path")

    # image
    p_img = sub.add_parser("image", help="Generate image")
    p_img.add_argument("prompt", help="Image description")
    p_img.add_argument("-o", "--output", help="Output file path")
    p_img.add_argument("--download", action="store_true", help="Download image file (default: url only)")
    p_img.add_argument("--aspect-ratio", help="Aspect ratio (e.g. 16:9, 1:1)")
    p_img.add_argument("--mode", choices=["t2i","i2i"], help="Generation mode")

    # music
    p_music = sub.add_parser("music", help="Generate music")
    p_music.add_argument("--prompt", required=True, help="Music style/prompt")
    p_music.add_argument("--lyrics", help="Song lyrics")
    p_music.add_argument("--instrumental", action="store_true", help="Instrumental only")
    p_music.add_argument("-o", "--output", help="Output file path")

    # video
    p_video = sub.add_parser("video", help="Generate video")
    p_video.add_argument("--prompt", required=True, help="Video description")
    p_video.add_argument("--mode", choices=["t2v","i2v","sef","ref"], help="Generation mode")
    p_video.add_argument("--duration", type=int, help="Duration in seconds (6-10)")
    p_video.add_argument("--first-frame", help="First frame image path")
    p_video.add_argument("-o", "--output", help="Output file path")

    # feishu
    p_feishu = sub.add_parser("feishu", help="Feishu group chat management")
    feishu_sub = p_feishu.add_subparsers(dest="feishu_sub", help="Feishu subcommands")
    p_list = feishu_sub.add_parser("list", help="List all bot groups")
    p_send = feishu_sub.add_parser("send", help="Send file to selected group")
    p_send.add_argument("file", help="File path to send (image/audio/video)")

    return parser


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Dispatch
    {
        "setup": cmd_setup,
        "check": cmd_check,
        "env": cmd_env,
        "tts": cmd_tts,
        "image": cmd_image,
        "music": cmd_music,
        "video": cmd_video,
        "feishu": cmd_feishu,
    }[args.command](args)


if __name__ == "__main__":
    main()
