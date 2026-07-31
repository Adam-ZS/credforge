# Contributing to CredForge

Thanks for taking the time to contribute! CredForge is a small, focused tool — the whole runtime is a single zero-dependency Python file. That constraint keeps it easy to audit, easy to fork, and easy to run anywhere.

## Ground rules

- **Zero dependencies.** Everything must stay in the Python 3.6+ standard library. A PR that adds a `requirements.txt` will be sent back.
- **No real data.** CredForge generates *synthetic* credentials. Never include passwords, emails, or PII sourced from actual breaches, leaks, or scrapes.
- **Keep it single-file.** Core generation logic lives in `credforge.py`. If a change needs a second module, argue for it in the PR description — it needs a strong reason.
- **Realism over volume.** The value of this tool is statistical realism: frequency-weighted passwords, per-country domains, age-weighted birth years. Changes that make output *more* like real breach data are welcome; changes that make it more random are not.

## Reporting bugs

Open an issue using the bug report template. Include:

- The exact command you ran
- The output (or the first few lines of it)
- Python version (`python3 --version`)
- What you expected vs. what happened

## Suggesting features

Open an issue using the feature request template. Explain the use case and why it fits the project's scope (red team simulations, detection validation, tool testing).

## Development workflow

1. Fork the repo and create a branch: `git checkout -b feature/your-change`
2. Make your change in `credforge.py`
3. Test it:
   ```bash
   python3 credforge.py -n 25 -f 1 -o /tmp/test.txt -q && wc -l /tmp/test.txt
   python3 credforge.py -n 25 -f 6 -o /tmp/test6.txt -q --min-length 8 && wc -l /tmp/test6.txt
   ```
   All six output formats should generate cleanly.
4. Update the README's feature table and CLI reference if the change affects the interface.
5. Commit with a clear message (`feat:`, `fix:`, `docs:`, `refactor:` prefixes).
6. Open a PR against `main` using the pull request template.

## Style

- Python 3.6-compatible syntax (no walrus, no `match`).
- Type hints welcome but not required.
- Functions stay small; generation logic is grouped by concern (names, domains, passwords, output).
- Comments explain *why*, not *what*.

## Licensing

By contributing, you agree your contributions are licensed under the MIT License (see LICENSE).
