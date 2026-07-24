#!/usr/bin/env python3
"""
PWLGen v2 -- Personalized Wordlist Generator (Advanced)

A CLI tool for generating and ranking targeted password wordlists for
authorized penetration testing / password-audit engagements.

Only use against systems and accounts you own or are explicitly
authorized to test.
"""

import argparse
import json
import sys
from datetime import datetime

from . import generator, scorer, hashcat_export

try:
    from . import hibp
    HIBP_AVAILABLE = True
except ImportError:
    HIBP_AVAILABLE = False

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class _Dummy:
        def __getattr__(self, name):
            return ""
    Fore = Style = _Dummy()

try:
    import pyfiglet
    HAS_FIGLET = True
except ImportError:
    HAS_FIGLET = False


def banner():
    if HAS_FIGLET:
        print(Fore.CYAN + pyfiglet.figlet_format("PWLGen", font="slant"))
    else:
        print(Fore.CYAN + "=== PWLGen v2 ===")
    print(Fore.YELLOW + "Personalized Wordlist Generator -- Advanced"
          + Style.RESET_ALL)
    print(Fore.YELLOW + "For authorized security testing only.\n")


def prompt(field, required=True):
    val = input(f"{Fore.GREEN}[?] {field}: {Style.RESET_ALL}").strip()
    if required and not val:
        return None
    return val


def gather_inputs_interactive():
    print(Fore.MAGENTA + "--- Target Profile Info ---" + Style.RESET_ALL)
    data = {
        "name": prompt("First name"),
        "surname": prompt("Last name / surname", required=False),
        "nickname": prompt("Nickname", required=False),
        "pet": prompt("Pet name", required=False),
        "dob": prompt("Date of birth (DDMMYYYY or blank)", required=False),
        "partner": prompt("Partner/spouse name", required=False),
        "custom": prompt("Any other keyword", required=False),
    }
    return {k: v for k, v in data.items() if v}


def load_profile_from_json(path):
    with open(path) as f:
        return json.load(f)


def save_profile_to_json(profile, path):
    with open(path, "w") as f:
        json.dump(profile, f, indent=2)


def build_arg_parser():
    p = argparse.ArgumentParser(
        prog="pwlgen",
        description="Generate and rank targeted password wordlists "
                     "from profile data. Authorized use only.",
    )
    p.add_argument("--profile", "-p", type=str,
                    help="Path to a JSON profile file (skips interactive prompts)")
    p.add_argument("--save-profile", type=str,
                    help="Save the (interactively entered) profile to this JSON path")
    p.add_argument("--out", "-o", type=str, default=None,
                    help="Output wordlist filename (default: timestamped)")
    p.add_argument("--min-len", type=int, default=4)
    p.add_argument("--max-len", type=int, default=24)
    p.add_argument("--no-keyboard-walks", action="store_true",
                    help="Disable keyboard-walk pattern splicing")
    p.add_argument("--top", type=int, default=None,
                    help="Only output the top N candidates by guessability rank")
    p.add_argument("--rank", action="store_true",
                    help="Rank output by guessability score (most likely first)")
    p.add_argument("--hashcat-rules", type=str, default=None,
                    help="Also write a Hashcat rule file to this path")
    p.add_argument("--hibp-check", type=int, default=0,
                    help="Check top N candidates against HaveIBeenPwned "
                         "(requires network + `requests`)")
    p.add_argument("--quiet", "-q", action="store_true",
                    help="Suppress banner and sample output")
    return p


def main(argv=None):
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if not args.quiet:
        banner()

    if args.profile:
        profile = load_profile_from_json(args.profile)
    else:
        profile = gather_inputs_interactive()
        if args.save_profile:
            save_profile_to_json(profile, args.save_profile)
            print(Fore.CYAN + f"[*] Profile saved to {args.save_profile}")

    if not profile:
        print(Fore.RED + "[!] No profile data provided. Exiting.")
        sys.exit(1)

    print(Fore.CYAN + "\n[*] Generating candidate wordlist..." + Style.RESET_ALL)
    candidates = generator.build_wordlist(
        profile,
        min_len=args.min_len,
        max_len=args.max_len,
        include_keyboard_walks=not args.no_keyboard_walks,
    )
    print(Fore.GREEN + f"[+] {len(candidates)} raw candidates generated")

    output_list = candidates
    ranked = None
    if args.rank or args.top:
        profile_words = [v for k, v in profile.items() if k != "dob"]
        ranked = scorer.rank_candidates(candidates, profile_words, top_n=args.top)
        output_list = [pw for pw, _, _ in ranked]
        print(Fore.GREEN + f"[+] Ranked by guessability score "
              f"(showing {len(output_list)})")

    out_name = args.out or f"wordlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(out_name, "w") as f:
        f.write("\n".join(output_list))
    print(Fore.GREEN + f"[+] Wordlist saved to: {out_name}")

    if args.hashcat_rules:
        n_rules = hashcat_export.write_rule_file(args.hashcat_rules)
        print(Fore.GREEN + f"[+] Hashcat rule file written: "
              f"{args.hashcat_rules} ({n_rules} rules)")

    if args.hibp_check:
        if not HIBP_AVAILABLE:
            print(Fore.RED + "[!] `requests` not installed -- skipping HIBP check")
        else:
            print(Fore.CYAN + f"\n[*] Checking top {args.hibp_check} candidates "
                  "against HaveIBeenPwned...")
            subset = output_list[:args.hibp_check]
            results = hibp.bulk_check(subset, limit=args.hibp_check)
            for pw, count in results.items():
                if count is None:
                    print(Fore.YELLOW + f"  {pw}: check failed (no network?)")
                elif count > 0:
                    print(Fore.RED + f"  {pw}: seen in {count} breaches")
                else:
                    print(Fore.WHITE + f"  {pw}: not found in breach corpus")

    if not args.quiet:
        print(Fore.YELLOW + "\nSample entries:")
        for w in output_list[:10]:
            print(Fore.WHITE + f"  {w}")
        if ranked:
            print(Fore.YELLOW + "\nTop 5 by guessability score "
                  "(lower = attacker tries first):")
            for pw, gscore, ent in ranked[:5]:
                print(Fore.WHITE +
                      f"  {pw:<20} score={gscore:<6} entropy={ent} bits")


if __name__ == "__main__":
    main()
