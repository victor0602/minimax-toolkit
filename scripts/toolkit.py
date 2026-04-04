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

Examples:
    python3 scripts/toolkit.py check --json          # Agent: get all status
    python3 scripts/toolkit.py setup                  # First-run setup
    python3 scripts/toolkit.py tts "hello world"     # Quick TTS
    python3 scripts/toolkit.py image "a cat"         # Quick image
    python3 scripts/toolkit.py env --show           # Show current config
"""
import sys
import os
import json
import subprocess
import argparse
import shlex
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
    }[args.command](args)


if __name__ == "__main__":
    main()
