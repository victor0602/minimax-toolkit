#!/usr/bin/env python3
"""
MiniMax image-01 generation wrapper
Usage: python3 image_generate.py "<prompt>" [-o output.png]
"""
import sys, os

USER_HOME = os.path.expanduser("~")
WORKSPACE = os.path.join(USER_HOME, ".openclaw/workspace")
SKILL_SCRIPT = os.path.join(USER_HOME, ".openclaw/workspace/skills/minimax-multimodal/scripts/image_generate.py")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python3 image_generate.py "<prompt>" [-o output.png]')
        sys.exit(1)

    prompt = sys.argv[1]
    output = "minimax-output/image.png"

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "-o" and i+1 < len(sys.argv):
            output = sys.argv[i+1]
            i += 2
        else:
            i += 1

    import subprocess
    result = subprocess.run(
        ["python3", SKILL_SCRIPT, prompt, "-o", output],
        cwd=WORKSPACE, capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)
