#!/usr/bin/env python3
"""
MiniMax TTS wrapper
Usage: python3 tts.py tts "text" [-v voice] [-o output]
"""
import sys, os, subprocess

USER_HOME = os.path.expanduser("~")
WORKSPACE = os.path.join(USER_HOME, ".openclaw/workspace")
SKILL_MULTIMODAL = os.path.join(USER_HOME, ".openclaw/workspace/skills/minimax-multimodal")

def tts(text, voice="female-shaonv", output="minimax-output/output.mp3"):
    env = os.environ.copy()
    if not env.get("MINIMAX_API_KEY"):
        print("[Error] MINIMAX_API_KEY not set. Set it in environment or in your shell profile.", file=sys.stderr)
        return False
    env.setdefault("MINIMAX_API_HOST", "https://api.minimaxi.com")
    voice_arg = ["-v", voice] if voice else []
    output_arg = ["-o", output]
    result = subprocess.run(
        ["python3", f"{SKILL_MULTIMODAL}/scripts/tts/generate_voice.py", "tts", text] + voice_arg + output_arg,
        cwd=WORKSPACE, env=env, capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] != "tts":
        print("Usage: python3 tts.py tts <text> [-v voice] [-o output]")
        sys.exit(1)

    text = sys.argv[2]
    voice, output = "female-shaonv", "minimax-output/output.mp3"
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == "-v" and i+1 < len(sys.argv):
            voice, i = sys.argv[i+1], i+2
        elif sys.argv[i] == "-o" and i+1 < len(sys.argv):
            output, i = sys.argv[i+1], i+2
        else:
            i += 1

    success = tts(text, voice, output)
    sys.exit(0 if success else 1)
