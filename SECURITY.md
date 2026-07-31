# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 3.x     | ✅ |
| 2.x     | ❌ (migrate to 3.0+) |
| 1.x     | ❌ |

## Reporting a vulnerability

CredForge is a credential generator for authorized red team operations. Its output is synthetic — but the tool itself could still have bugs worth reporting (logic errors, incorrect format output, edge cases that crash, or anything that could produce *real* data by accident).

**Please do not open a public issue for security bugs.** Report privately to:

- **GitHub private vulnerability reporting:** https://github.com/Adam-ZS/credforge/security/advisories/new
- **Email:** Adam-ZS@users.noreply.github.com

### What to include

- The version affected (`python3 credforge.py --version`)
- A minimal reproduction (command + input)
- Impact description
- Suggested fix, if you have one

### Response timeline

- **Acknowledgment:** within 48 hours
- **Initial assessment:** within 5 business days
- **Fix / mitigation:** as soon as possible, coordinated with disclosure

You'll be credited for the report unless you prefer to stay anonymous.

## Scope

The following are **not** security vulnerabilities:

- Using the tool against systems you don't own or aren't authorized to test
- The existence of "weak" passwords in output — that's the intended realism model (use `--min-length` to filter)
- Synthetic SSN/credit card values being format-valid — they are not real, issued, or usable
