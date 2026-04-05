#!/usr/bin/env python3
# MIT License — Copyright (c) 2026 Victor
# https://github.com/victor0602/minimax-toolkit

"""
Environment and infrastructure tests for MiniMax Toolkit.
Run: python3 scripts/test_env.py
"""
import sys
import os
import subprocess
import shutil
from pathlib import Path

# Add scripts dir to path for imports
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

import toolkit

PASS = "\033[0;32m✓\033[0m"
FAIL = "\033[0;31m✗\033[0m"
WARN = "\033[0;33m⚠\033[0m"


def test_dependencies():
    """Test all system dependencies are installed."""
    print("\n[Test] System Dependencies")
    deps = ["jq", "curl", "ffmpeg", "python3", "base64"]
    all_ok = True
    for dep in deps:
        if shutil.which(dep):
            ver = subprocess.run([dep, "--version"], capture_output=True, text=True).stdout[:30]
            print(f"  {PASS} {dep}: {ver.split(chr(10))[0]}")
        else:
            print(f"  {FAIL} {dep}: not found")
            all_ok = False
    return all_ok


def test_project_structure():
    """Test project structure is intact."""
    print("\n[Test] Project Structure")
    project_root = SCRIPT_DIR.parent
    required_paths = [
        "scripts/toolkit.py",
        "scripts/setup.sh",
        "scripts/check.sh",
        "scripts/tts.py",
        "scripts/image_generate.py",
        "scripts/lib/common.sh",
        "scripts/lib/diagnose.sh",
        "scripts/tts/generate_voice.sh",
        "scripts/image/generate_image.sh",
        "scripts/music/generate_music.sh",
        "scripts/video/generate_video.sh",
    ]
    all_ok = True
    for path in required_paths:
        full_path = project_root / path
        if full_path.exists():
            print(f"  {PASS} {path}")
        else:
            print(f"  {FAIL} {path}: missing")
            all_ok = False
    return all_ok


def test_config_file():
    """Test .env configuration."""
    print("\n[Test] Configuration File")
    project_root = SCRIPT_DIR.parent
    env_file = project_root / ".env"
    if env_file.exists():
        print(f"  {PASS} .env exists")
        # Load and check key
        toolkit.load_env()
        api_key = os.environ.get("MINIMAX_API_KEY", "")
        if api_key and api_key not in ("sk-cp-xxx", "sk-api-xxx", "YOUR_API_KEY"):
            masked = api_key[:8] + "..."
            print(f"  {PASS} API key present: {masked}")
            return True
        else:
            print(f"  {WARN} API key not set or is placeholder")
            return False
    else:
        print(f"  {FAIL} .env not found")
        print(f"       Run: python3 scripts/toolkit.py doctor --fix")
        return False


def test_imports():
    """Test all required Python imports."""
    print("\n[Test] Python Imports")
    required_modules = ["json", "subprocess", "argparse", "pathlib", "requests"]
    all_ok = True
    for mod in required_modules:
        try:
            __import__(mod)
            print(f"  {PASS} {mod}")
        except ImportError:
            print(f"  {FAIL} {mod}: not found")
            all_ok = False
    return all_ok


def test_shell_scripts():
    """Test shell scripts have correct permissions and syntax."""
    print("\n[Test] Shell Scripts Syntax")
    project_root = SCRIPT_DIR.parent
    scripts = [
        "scripts/setup.sh",
        "scripts/check.sh",
        "scripts/install-mcporter.sh",
        "scripts/lib/common.sh",
        "scripts/lib/diagnose.sh",
        "scripts/tts/generate_voice.sh",
        "scripts/image/generate_image.sh",
        "scripts/music/generate_music.sh",
        "scripts/video/generate_video.sh",
    ]
    all_ok = True
    for script in scripts:
        path = project_root / script
        if not path.exists():
            print(f"  {FAIL} {script}: not found")
            all_ok = False
            continue
        # Check syntax with bash -n
        result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  {PASS} {script}")
        else:
            print(f"  {FAIL} {script}: syntax error - {result.stderr}")
            all_ok = False
    return all_ok


def test_toolkit_commands():
    """Test toolkit command structure."""
    print("\n[Test] Toolkit Command Structure")
    project_root = SCRIPT_DIR.parent
    toolkit_py = project_root / "scripts/toolkit.py"
    if not toolkit_py.exists():
        print(f"  {FAIL} toolkit.py not found")
        return False

    # Test --help
    result = subprocess.run(
        ["python3", str(toolkit_py), "--help"],
        capture_output=True, text=True, cwd=str(project_root)
    )
    if result.returncode == 0:
        print(f"  {PASS} toolkit.py --help works")
    else:
        print(f"  {FAIL} toolkit.py --help failed")
        return False

    # Test all commands are present
    expected_commands = ["setup", "check", "doctor", "env", "tts", "image", "music", "video", "feishu"]
    output = result.stdout
    all_ok = True
    for cmd in expected_commands:
        if cmd in output:
            print(f"  {PASS} '{cmd}' command found")
        else:
            print(f"  {FAIL} '{cmd}' command missing")
            all_ok = False
    return all_ok


def test_doctor_command():
    """Test doctor command works."""
    print("\n[Test] Doctor Command")
    project_root = SCRIPT_DIR.parent
    toolkit_py = project_root / "scripts/toolkit.py"
    result = subprocess.run(
        ["python3", str(toolkit_py), "doctor"],
        capture_output=True, text=True, cwd=str(project_root),
        env={**os.environ, "MINIMAX_API_KEY": os.environ.get("MINIMAX_API_KEY", "sk-cp-test")}
    )
    output = result.stdout + result.stderr
    if result.returncode in (0, 1):  # 0 = all ok, 1 = issues found
        print(f"  {PASS} doctor command runs (exit: {result.returncode})")
        # Check for key sections
        checks = ["Checking system dependencies", "Checking API key", "Summary"]
        for check in checks:
            if check in output:
                print(f"  {PASS} {check}")
            else:
                print(f"  {WARN} {check}: not found in output")
        return True
    else:
        print(f"  {FAIL} doctor command failed unexpectedly")
        print(f"       {output[:200]}")
        return False


def main():
    print("=" * 50)
    print("MiniMax Toolkit — Environment Tests")
    print("=" * 50)

    results = []

    results.append(("Dependencies", test_dependencies()))
    results.append(("Project Structure", test_project_structure()))
    results.append(("Python Imports", test_imports()))
    results.append(("Shell Scripts", test_shell_scripts()))
    results.append(("Toolkit Commands", test_toolkit_commands()))
    results.append(("Doctor Command", test_doctor_command()))
    results.append(("Config File", test_config_file()))

    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)
    all_pass = True
    for name, ok in results:
        status = f"{PASS} PASS" if ok else f"{FAIL} FAIL"
        print(f"  {status}  {name}")
        if not ok:
            all_pass = False

    print()
    if all_pass:
        print(f"{PASS} All environment tests passed!")
        return 0
    else:
        print(f"{FAIL} Some environment tests failed. Run 'python3 scripts/toolkit.py doctor' for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
