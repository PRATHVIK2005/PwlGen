"""
Core generation engine: leetspeak permutations, keyboard-walk patterns,
date-token extraction, and combinatorial profile-field mixing.
"""

import itertools

LEET_MAP = {
    "a": ["a", "@", "4"],
    "e": ["e", "3"],
    "i": ["i", "1", "!"],
    "o": ["o", "0"],
    "s": ["s", "$", "5"],
    "t": ["t", "7"],
    "g": ["g", "9"],
    "b": ["b", "8"],
    "l": ["l", "1"],
}

COMMON_SUFFIXES = [
    "", "!", "@", "#", "123", "1234", "12345", "007", "69", "99",
    "01", "02", "!!", "@123", "2024", "2025", "2026",
]

COMMON_PREFIXES = ["", "@", "#"]

# Separators people commonly use to join two pieces of personal info
# into a password (e.g. Name@DDMM, Name_YYYY, Name-1999).
SEPARATORS = ["", "@", "_", ".", "-", "#"]

# Common keyboard-walk substrings people fall back to as password filler,
# grouped by row/pattern so we can splice them onto profile words.
KEYBOARD_WALKS = [
    "qwerty", "asdf", "zxcv", "qazwsx", "1qaz2wsx",
    "!qaz@wsx", "qwerty123", "asdf1234",
]


def leet_variants(word, max_variants=8):
    """Generate a bounded set of leetspeak variants for a word.

    Uses combinatorial substitution across all eligible characters,
    capped at max_variants to avoid exponential blowup on long words.
    """
    word = word.lower()
    positions = [i for i, c in enumerate(word) if c in LEET_MAP]
    if not positions:
        return {word}

    variants = {word}

    full = list(word)
    for i in positions:
        alts = LEET_MAP[full[i]]
        if len(alts) > 1:
            full[i] = alts[1]
    variants.add("".join(full))

    count = 0
    for combo in itertools.product(*[LEET_MAP[word[i]] for i in positions]):
        if count >= max_variants:
            break
        chars = list(word)
        for pos, repl in zip(positions, combo):
            chars[pos] = repl
        variants.add("".join(chars))
        count += 1

    return variants


def case_variants(word):
    return {word.lower(), word.capitalize(), word.upper()}


def date_tokens(dob):
    """Extract year/day/month tokens from a DDMMYYYY or YYYY string."""
    tokens = set()
    digits = "".join(c for c in dob if c.isdigit())
    if len(digits) == 8:
        dd, mm, yyyy = digits[:2], digits[2:4], digits[4:]
        tokens.update([yyyy, yyyy[2:], dd + mm, mm + dd, dd, mm])
    elif len(digits) == 4:
        tokens.add(digits)
        tokens.add(digits[2:])
    return tokens


def keyboard_walk_variants(word):
    """Splice common keyboard-walk substrings onto a base word."""
    out = set()
    for walk in KEYBOARD_WALKS:
        out.add(f"{word}{walk}")
        out.add(f"{walk}{word}")
    return out


def separator_join_variants(word, token, separators=SEPARATORS, include_cases=True):
    """
    Explicitly generate word+separator+token combinations in both
    orders and (optionally) across case variants of the word, e.g.
    for word="Prathvik", token="1706" ->
        Prathvik@1706, Prathvik_1706, Prathvik.1706, Prathvik-1706,
        Prathvik#1706, Prathvik1706, prathvik@1706, PRATHVIK@1706,
        1706@Prathvik, ... etc.

    This models one of the most common real-world password patterns:
    a name/word joined to a date/number with a single separator
    character, rather than relying on leetspeak or suffix stacking
    to accidentally produce the same shape.
    """
    out = set()
    words_to_use = case_variants(word) if include_cases else {word}
    for w in words_to_use:
        for sep in separators:
            out.add(f"{w}{sep}{token}")
            out.add(f"{token}{sep}{w}")
    return out


def separator_join_word_pairs(word_a, word_b, separators=SEPARATORS):
    """Same idea as separator_join_variants, but for two profile words
    (e.g. Name@Surname, Name_Pet) rather than a word + date token."""
    out = set()
    for sep in separators:
        out.add(f"{word_a}{sep}{word_b}")
        out.add(f"{word_b}{sep}{word_a}")
    return out


def build_wordlist(profile, min_len=4, max_len=24, include_keyboard_walks=True):
    """
    profile: dict of field -> value, e.g.
        {"name": "Rajesh", "surname": "Kumar", "dob": "15081999"}
    Returns a sorted list of candidate passwords.
    """
    base_words = {
        v for k, v in profile.items()
        if k != "dob" and v
    }

    extra_tokens = set()
    if profile.get("dob"):
        extra_tokens |= date_tokens(profile["dob"])

    all_words = set()
    for word in base_words:
        for cased in case_variants(word):
            all_words.add(cased)
            all_words |= leet_variants(cased)

    # Explicit separator-joined combinations: Name@DDMM, name_YYYY, etc.
    # This is kept as its own pass (not just a side-effect of leetspeak
    # or suffix-stacking) because word+separator+date is one of the
    # single most common real-world password patterns.
    separator_combos = set()
    for word in base_words:
        for tok in extra_tokens:
            separator_combos |= separator_join_variants(word, tok)

    # Pairwise combination of base words -- now using the full
    # separator set (@, _, ., -, #, and no separator) instead of a
    # narrow hardcoded subset.
    combined = set()
    word_list = list(base_words)
    for a, b in itertools.permutations(word_list, 2):
        combined |= separator_join_word_pairs(a, b)
    all_words |= combined
    all_words |= separator_combos

    if include_keyboard_walks:
        walk_variants = set()
        for w in list(all_words)[:20]:  # cap to keep this bounded
            walk_variants |= keyboard_walk_variants(w)
        all_words |= walk_variants

    final = set()
    for w in all_words:
        for suf in COMMON_SUFFIXES:
            final.add(f"{w}{suf}")
        for pre in COMMON_PREFIXES:
            final.add(f"{pre}{w}")
        for tok in extra_tokens:
            final.add(f"{w}{tok}")
            final.add(f"{tok}{w}")
            for suf in ("!", "@", ""):
                final.add(f"{w}{tok}{suf}")

    final = {w for w in final if min_len <= len(w) <= max_len}
    return sorted(final)