# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability within MiniMax Toolkit, please report it responsibly.

**Please do NOT create a public GitHub issue for security vulnerabilities.**

Instead, contact the maintainer directly via:
- GitHub Security Advisories: https://github.com/victor0602/minimax-toolkit/security/advisories/new
- Or send a private report through GitHub

All security reports will be acknowledged within 48 hours and you will receive a more detailed response within 7 days.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.5.x   | :white_check_mark: |

## Security Best Practices

When using this toolkit:

1. **Never commit your API keys** — Use environment variables or a `.env` file (already in `.gitignore`)
2. **Rotate keys regularly** — If a key is exposed, rotate it immediately via the MiniMax dashboard
3. **Set appropriate file permissions** — Your `.env` file should be `chmod 600`
4. **Use least-privilege access** — Only grant the permissions your bot actually needs in Feishu

## Known Security Considerations

### API Keys
- MiniMax API keys grant access to your account's AI services
- Feishu App credentials control your bot's permissions in workspaces
- Treat all credentials as sensitive secrets — never log or expose them

### Command Injection
- All user-supplied paths are validated via `validate_output_path()` to prevent path traversal
- Shell scripts use `set -euo pipefail` to fail safely on errors

### Temporary Files
- `generate_voice.sh` creates temporary files in a `tmp/` subdirectory alongside the output, cleaned up via `trap` on EXIT/INT/TERM signals
- `generate_video.sh`, `generate_long_video.sh`, `generate_template_video.sh` also use trap-based cleanup for temp directories
- Interrupt handlers (Ctrl+C) also trigger cleanup via `trap`
