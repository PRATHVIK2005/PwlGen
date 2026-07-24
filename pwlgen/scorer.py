"""
Scores and ranks candidate passwords by estimated crack-likelihood.

This isn't a cryptographic entropy calculation (that would favor pure
randomness, which is the opposite of what we want here). Instead it's
a heuristic "targeted-guess likelihood" score: candidates that closely
resemble realistic human password patterns (profile word + short
suffix) rank higher than long, deeply-mutated strings, because a real
password-guesser would try the short, obvious ones first.
"""

import math
import re

CHAR_CLASS_PATTERNS = [
    re.compile(r"[a-z]"),
    re.compile(r"[A-Z]"),
    re.compile(r"[0-9]"),
    re.compile(r"[^a-zA-Z0-9]"),
]


def charset_size(password):
    size = 0
    if re.search(r"[a-z]", password):
        size += 26
    if re.search(r"[A-Z]", password):
        size += 26
    if re.search(r"[0-9]", password):
        size += 10
    if re.search(r"[^a-zA-Z0-9]", password):
        size += 32
    return max(size, 1)


def shannon_entropy_bits(password):
    """Classic entropy estimate: log2(charset_size) * length."""
    return len(password) * math.log2(charset_size(password))


def guessability_score(password, profile_words):
    """
    Lower score = more likely to be guessed early by an attacker using
    this exact wordlist strategy (i.e. "high priority" candidate).

    Heuristics:
    - Shorter passwords score lower (attackers try short first).
    - Passwords that are an exact profile word + short common suffix
      score lower (most realistic human pattern).
    - Passwords with many leet substitutions score higher (less likely
      a real user typed something that convoluted).
    """
    score = len(password) * 1.0

    leet_chars = sum(1 for c in password if c in "@$!01345789")
    score += leet_chars * 0.8

    for w in profile_words:
        if password.lower().startswith(w.lower()):
            score -= 3.0
            break

    return round(score, 2)


def rank_candidates(candidates, profile_words, top_n=None):
    """
    Returns list of (password, guessability_score, entropy_bits) tuples
    sorted by guessability_score ascending (most likely first).
    """
    scored = [
        (pw, guessability_score(pw, profile_words), round(shannon_entropy_bits(pw), 1))
        for pw in candidates
    ]
    scored.sort(key=lambda t: t[1])
    if top_n:
        scored = scored[:top_n]
    return scored
