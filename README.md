# PwdGen — Personalized Wordlist Generator



A modular CLI tool that generates, ranks, and exports **targeted**
password wordlists from profile data (name, DOB, pet, partner, etc.)
for authorized password auditing and penetration testing engagements.

Unlike generic wordlists (`rockyou.txt` and friends), which only catch
weak/common passwords, PwdGen models how real people actually build
passwords — a name, a birth year, a leetspeak swap, a common suffix —
and generates the candidates an attacker (or an auditor) would realistically
try first.

> ⚠️ **For authorized security testing only.** See [Legal / Ethical Use](#legal--ethical-use).

---

## Table of Contents

- [Features](#features)
- [Why the ranking matters](#why-the-ranking-matters)
- [Installation](#installation)
- [Usage](#usage)
- [CLI Reference](#cli-reference)
- [Testing](#testing)
- [Roadmap](#roadmap)
- [Legal / Ethical Use](#legal--ethical-use)


---

## Features

- **Leetspeak permutation engine** — combinatorial substitution
  (`a→@/4`, `s→$/5`, `i→1/!`, etc.), bounded to avoid exponential blowup
- **Keyboard-walk splicing** — common filler patterns (`qwerty`, `1qaz2wsx`)
  appended/prepended to profile-derived words
- **Date-token extraction** — pulls year/day/month combinations from a DOB
- **Pairwise profile combination** — mixes fields like `name+partner`,
  `name.pet`, `nickname_surname`
- **Guessability scoring** — ranks candidates by realistic likelihood,
  not just raw entropy (see [below](#why-the-ranking-matters))
- **Hashcat rule export** — emits a real `.hcrule` file so the mutation
  logic can run natively inside Hashcat
- **HaveIBeenPwned integration** — checks top candidates against known
  breaches via the privacy-preserving k-anonymity API
- **Scriptable CLI** — JSON profile save/load, full `argparse` interface,
  quiet mode for automation
- **17 passing unit tests** (pytest) + CI on every push (GitHub Actions
  and GitLab CI)



## Why the ranking matters

A raw wordlist tells you nothing about *which* password to try first.
`scorer.py` implements a heuristic **guessability score**: short,
minimally-mutated candidates that closely match a profile word (e.g.
`Tiger99`) score lower — meaning *try first* — than deeply
leet-substituted, long candidates (e.g. `T!g3r@#$1999xyz`), because
that mirrors how real users actually pick passwords.

This is intentionally the *opposite* of classic Shannon entropy, which
rewards randomness. Entropy is the right metric for measuring password
*strength* — it's the wrong metric for predicting what a targeted
attacker (or this tool) should try first. PwdGen reports both, but
ranks by guessability.

## Installation

```bash
git clone https://github.com/prathvikshetty17/PwdGen.git
cd PwdGen
pip install -r requirements.txt
```

## Usage

**Interactive mode:**
```bash
python3 -m pwlgen.cli
```

**Scripted mode with a saved profile:**
```bash
python3 -m pwlgen.cli --profile profile.json --rank --top 100 \
    --hashcat-rules rules.hcrule --out wordlist.txt
```

**Check top candidates against known breaches:**
```bash
python3 -m pwlgen.cli --profile profile.json --rank --hibp-check 20
```

### Sample output

```
[*] Generating candidate wordlist...
[+] 14822 raw candidates generated
[+] Ranked by guessability score (showing 15)
[+] Wordlist saved to: wordlist_20260724_201406.txt
[+] Hashcat rule file written: rules.hcrule (33 rules)

Top 5 by guessability score (lower = attacker tries first):
  KUMAR                score=5.0    entropy=23.5 bits
  Kumar                score=5.0    entropy=23.5 bits
  TIGER                score=5.0    entropy=23.5 bits
  Tiger                score=5.0    entropy=23.5 bits
  kumar                score=5.0    entropy=23.5 bits
```

## CLI Reference

| Flag | Description |
|---|---|
| `--profile PATH` | Load profile from JSON instead of prompting |
| `--save-profile PATH` | Save interactively-entered profile to JSON |
| `--out PATH` | Output wordlist filename |
| `--min-len` / `--max-len` | Length bounds for candidates |
| `--no-keyboard-walks` | Disable keyboard-walk splicing |
| `--rank` | Rank output by guessability score |
| `--top N` | Only keep top N ranked candidates |
| `--hashcat-rules PATH` | Also emit a Hashcat rule file |
| `--hibp-check N` | Check top N candidates against HaveIBeenPwned |
| `--quiet` | Suppress banner/sample output (for scripting) |

## Testing

```bash
python3 -m pytest tests/ -v
```

17/17 tests passing — covers leetspeak generation, date-token
extraction, keyboard-walk splicing, length filtering, entropy/
guessability scoring, ranking order, and Hashcat rule generation.
CI runs this suite automatically on every push (see the badge above).

## Roadmap

- [ ] Multiprocessing for large-scale generation (100k+ candidates)
- [ ] Mask-based generation mode (crunch-style `?l?l?l?d?d`)
- [ ] John the Ripper rule export alongside Hashcat
- [ ] Web-scraped OSINT enrichment — deferred pending careful scoping
      of privacy/consent boundaries

## Legal / Ethical Use

This tool is for **authorized** security testing, CTFs, and personal
password-hygiene audits only. Do not use it against accounts or systems
you do not own or do not have explicit written authorization to test.

The HaveIBeenPwned integration uses the k-anonymity range API — your
real password and its full hash are never transmitted, only a 5-character
SHA-1 hash prefix.

[GitHub](https://github.com/prathvikshetty17)
