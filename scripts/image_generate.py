#!/usr/bin/env python3
"""
MiniMax image-01 generation wrapper
Usage: python3 image_generate.py "<prompt>" [-o output.png]
"""
import sys
import os
import subprocess
import argparse

USER_HOME = os.path.expanduser("~")
WORKSPACE = os.path.join(USER_HOME, ".openclaw/workspace")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_SCRIPT = os.path.join(SCRIPT_DIR, "image", "generate_image.sh")


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


def generate_image(prompt, output="minimax-output/image.png", **kwargs):
    load_env()
    os.makedirs(os.path.dirname(os.path.abspath(output)) if os.path.dirname(output) else "minimax-output", exist_ok=True)

    cmd = ["bash", SKILL_SCRIPT, "--prompt", prompt, "-o", output]
    for k, v in kwargs.items():
        if v is not None:
            cmd.extend([f"--{k.replace('_', '-')}", str(v)])

    env = os.environ.copy()
    if not env.get("MINIMAX_API_KEY"):
        print("[Error] MINIMAX_API_KEY not set.", file=sys.stderr)
        return False

    result = subprocess.run(cmd, cwd=WORKSPACE, env=env, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="MiniMax image-01 生成工具")
    parser.add_argument("prompt", help="图片描述文本")
    parser.add_argument("-o", "--output", default="minimax-output/image.png", help="输出文件路径")
    parser.add_argument("--aspect-ratio", "--ratio", dest="aspect_ratio", help="画面比例，如 1:1, 16:9, 3:2")
    parser.add_argument("--mode", default="t2i", help="模式：t2i（文生图）或 i2i（图生图）")
    parser.add_argument("--ref-image", dest="ref_image", help="参考图片路径（i2i 模式用）")
    parser.add_argument("-n", type=int, help="生成数量")
    args = parser.parse_args()

    kwargs = {}
    if args.aspect_ratio:
        kwargs["aspect_ratio"] = args.aspect_ratio
    if args.mode:
        kwargs["mode"] = args.mode
    if args.ref_image:
        kwargs["ref_image"] = args.ref_image
    if args.n:
        kwargs["n"] = args.n

    success = generate_image(args.prompt, args.output, **kwargs)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
