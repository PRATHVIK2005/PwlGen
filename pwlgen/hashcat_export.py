"""
Exports base profile words as a Hashcat rule file, so the wordlist's
mutation logic (leet subs, suffixes) can be reapplied by Hashcat itself
against a *different* small base wordlist -- letting this tool serve
as a rule-generator, not just a static list generator.

Hashcat rule syntax reference (subset used here):
    $X       -> append character X
    ^X       -> prepend character X
    sXY      -> substitute all X with Y
    c        -> capitalize first letter
    u        -> uppercase all
    l        -> lowercase all
"""

SUB_RULES = {
    "a": "@", "s": "$", "i": "1", "o": "0", "e": "3", "t": "7",
}

SUFFIXES = ["123", "!", "007", "69", "99", "2025", "2026"]


def generate_rule_lines():
    """Generate a list of Hashcat rule strings covering our mutation
    strategy: case changes, char substitutions, and suffix appends."""
    lines = []

    # Base case transforms
    lines.append("")       # no-op (try as-is)
    lines.append("l")      # lowercase
    lines.append("u")      # uppercase
    lines.append("c")      # capitalize

    # Single-character substitutions
    for src, dst in SUB_RULES.items():
        lines.append(f"s{src}{dst}")
        lines.append(f"c s{src}{dst}")

    # Suffix appends (each char appended individually per hashcat syntax)
    for suf in SUFFIXES:
        rule = "".join(f"${ch}" for ch in suf)
        lines.append(rule)
        lines.append(f"c {rule}")

    # Combined: capitalize + substitute + suffix (a couple of examples)
    for suf in SUFFIXES[:3]:
        rule_suffix = "".join(f"${ch}" for ch in suf)
        lines.append(f"c sa@ {rule_suffix}")

    return lines


def write_rule_file(path):
    lines = generate_rule_lines()
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return len(lines)
