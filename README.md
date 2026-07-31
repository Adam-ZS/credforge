# ⚡ CredForge — Realistic Credential Generator

> *Combolist-grade synthetic credentials for red team operations*

[![Python 3.6+](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)](credforge.py)
[![Version](https://img.shields.io/badge/version-3.0.0-orange.svg)](https://github.com/Adam-ZS/credforge/releases)

CredForge generates realistic-looking `email:password` combinations that match the statistical patterns of actual data breaches. Frequency-weighted passwords (the real top-password tail), per-country email domains, age-weighted birth years, and optional PII/credit card generation for simulation exercises. **100% synthetic — no data from actual breaches.**

**Use cases:** Phishing simulations, red team credential harvesting demos, database population, tool testing, SOC detection validation.

---

## Features

| Feature | Details |
|---------|---------|
| **9 Countries** | US, UK, France, Germany, Russia, Middle East, Japan, Brazil, India |
| **1,260+ Names** | Culturally accurate first + last names per region |
| **Breach-weighted passwords** | Top real-world passwords dominate the tail; weighted bases + 20 generation patterns (leetspeak, seasons, birth dates, keyboard runs, special chars) |
| **Per-country domains** | Weighted by real registration distribution — gmail-heavy in US/IN, mail.ru in RU, bol.com.br in BR, web.de in DE, etc. |
| **PII (optional)** | Phone, full address, ZIP code, SSN (US), security questions + answers |
| **Credit Cards (optional)** | Luhn-valid format (Visa/MC/Amex/Discover) — **not real cards** |
| **6 Output Formats** | `email:pass` → `user:pass` → `email:pass:name` → full PII → full PII + CC → password-only wordlist |
| **Dedup** | `--unique` on by default — no repeated lines |
| **Filtering** | `--min-length` for spraying/cracking candidate lists |
| **Reproducible** | `--seed` for deterministic output |
| **Zero Dependencies** | Python 3.6+ standard library only |

---

## Quick Start

### Option 1 — pip install

```bash
pip install credforge
credforge --count 5000 --format 1 --country br --output brazil_creds.txt
```

### Option 2 — from source

```bash
git clone https://github.com/Adam-ZS/credforge
cd credforge
python3 credforge.py -n 5000 -f 1 -c br -o brazil_creds.txt
```

### Interactive mode

Run with no arguments for the guided prompt:

```bash
python3 credforge.py
```

```
  Lines to generate [100]: 5000

  Output format:
  1) email:password
  2) username:password
  3) email:password:fullname
  4) Full PII + SSN ⚠
  5) Full PII + SSN + CC ⚠⚠

  Format [1]: 1
  Country (blank=worldwide) [all]: br
  Output file [combolist.txt]: brazil_creds.txt

  Generating 5000 credentials...
  ✔ Saved brazil_creds.txt (186,204 bytes)
```

---

## CLI Reference

| Flag | Description | Default |
|------|-------------|---------|
| `-n, --count` | Lines to generate | `100` |
| `-f, --format` | `1` email:pass · `2` user:pass · `3` email:pass:name · `4` PII+SSN · `5` PII+SSN+CC · `6` password-only | `1` |
| `-c, --country` | Country code (`us`, `uk`, `fr`, `de`, `ru`, `ar`, `jp`, `br`, `in`) | worldwide |
| `-o, --output` | Output file path | `combolist.txt` |
| `--unique` / `--no-unique` | Deduplicate entries | on |
| `--min-length` | Minimum password length (spraying/cracking lists) | `0` |
| `--seed` | Random seed for reproducible output | random |
| `-q, --quiet` | Suppress sample output | off |
| `--version` | Show version | — |

---

## Sample Output

### Format 1 — email:password
```
marina.silva89@gmail.com:Summer1987!
lucas.oliveira73@yahoo.com.br:P@ssw0rd1992
joao24@bol.com.br:Admin%2001@
```

### Format 4 — Full PII + SSN
```
james.smith42@gmail.com:Winter1998!:James Smith:+1-305-472-8910:7423 Main St, Miami, FL 33101:492-81-7037
```

### Format 5 — Full PII + SSN + CC
```
maria.garcia22@yahoo.com:Passw0rd1974:Maria Garcia:+1-818-739-2041:1529 Oak Ave, Los Angeles, CA 90012:618-53-2091:4532418573947267:08/28:342
```

---

## Output Formats Detail

| Mode | Fields |
|------|--------|
| **1** | `email:password` |
| **2** | `username:password` |
| **3** | `email:password:full_name` |
| **4** | `email:password:full_name:phone:address:ssn` |
| **5** | `email:password:full_name:phone:address:ssn:cc_number:cc_expiry:cc_cvv` |
| **6** | `password` (one per line — wordlist / hashcat / password spraying) |

PII formats (4–5) may append `Q:security_question A:answer` (30% chance).

---

## Country Codes

| Code | Country | Domains Included |
|------|---------|-----------------|
| `us` | United States | gmail, yahoo, hotmail, aol, icloud |
| `uk` | United Kingdom | btinternet, virginmedia, sky, talktalk |
| `fr` | France | orange, free, sfr, wanadoo, laposte |
| `de` | Germany | t-online, web, gmx, freenet, 1und1 |
| `ru` | Russia | mail, yandex, rambler, bk |
| `jp` | Japan | yahoo.co.jp, docomo, ezweb, softbank |
| `br` | Brazil | bol, uol, ig, globo, terra |
| `in` | India | rediffmail, indiatimes, sify, yahoo.co.in |
| `ar` | Middle East | outlook.sa, yahoo, hotmail |

Leave blank for worldwide (weighted distribution).

---

## Requirements

- Python 3.6+
- Standard library only — zero dependencies

---

## Wiki

See the [wiki](https://github.com/Adam-ZS/credforge/wiki) for use cases, integration recipes, and FAQ.

---

## Disclaimer

All credentials generated by CredForge are **synthetic and randomized**. They do not correspond to real individuals or accounts. No data is sourced from actual breaches. This tool is intended for **authorized security testing, simulation exercises, and educational purposes only.**

---

## License

[MIT](LICENSE) — © 2026 Adam ZS
