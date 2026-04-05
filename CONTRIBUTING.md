# Contributing to MiniMax Toolkit

Thank you for your interest in contributing!

## Getting Started

```bash
git clone https://github.com/victor0602/minimax-toolkit.git
cd minimax-toolkit
python3 scripts/toolkit.py setup
```

## Development

```bash
# Run environment checks
python3 scripts/toolkit.py doctor --fix

# Run tests
python3 scripts/test_env.py
python3 scripts/test_features.py
```

## Project Structure

```
scripts/
├── toolkit.py           # Unified CLI entry point
├── lib/
│   ├── common.sh        # Shared functions (load_env, validate_output_path, error_exit)
│   ├── diagnose.sh      # Diagnostic functions (JSON output)
│   └── feishu.py        # Feishu API shared library
├── tts/                 # Voice generation
├── image/               # Image generation
├── music/               # Music generation
└── video/               # Video generation
```

## Coding Standards

### Shell Scripts
- Use `set -euo pipefail`
- Source `lib/common.sh` for shared functions
- All error exits must return non-zero exit codes
- Output JSON status lines via `_json_status` (from `diagnose.sh`)

### Python Scripts
- Use `#!/usr/bin/env python3` shebang
- Import `scripts.lib.feishu` for Feishu API calls
- No hardcoded credentials — read from environment variables

### Commit Messages
- Use Chinese or English, keep subject line under 72 characters
- Reference issues with `#number` when applicable

## Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Make changes and test
4. Commit with a clear message
5. Push and open a Pull Request

## Reporting Issues

When reporting bugs, include:
- Output of `python3 scripts/toolkit.py check --json`
- The command that failed
- Expected vs actual behavior
