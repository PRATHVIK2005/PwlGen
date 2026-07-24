"""
Cross-checks candidate passwords against the HaveIBeenPwned
Pwned Passwords database using the k-anonymity API.

How k-anonymity works here (important -- this is what makes it safe
to use without leaking the real password to a third party):
    1. SHA-1 hash the password locally.
    2. Send only the first 5 hex characters of the hash to the API.
    3. The API returns all hash suffixes that share that 5-char prefix,
       along with how many times each has appeared in known breaches.
    4. We check locally whether our full hash suffix is in that list.

The plaintext password and the full hash never leave your machine.
Requires network access to api.pwnedpasswords.com.
"""

import hashlib

try:
    import requests
except ImportError:
    requests = None

HIBP_RANGE_URL = "https://api.pwnedpasswords.com/range/{prefix}"


def sha1_hash(password):
    return hashlib.sha1(password.encode("utf-8")).hexdigest().upper()


def check_password(password, timeout=5):
    """
    Returns breach count (int) if the password appears in known
    breaches, 0 if not found, or None if the check couldn't be
    performed (no network / library missing).
    """
    if requests is None:
        return None

    full_hash = sha1_hash(password)
    prefix, suffix = full_hash[:5], full_hash[5:]

    try:
        resp = requests.get(
            HIBP_RANGE_URL.format(prefix=prefix), timeout=timeout
        )
        resp.raise_for_status()
    except Exception:
        return None

    for line in resp.text.splitlines():
        hash_suffix, count = line.split(":")
        if hash_suffix == suffix:
            return int(count)

    return 0


def bulk_check(passwords, limit=50, timeout=5):
    """
    Checks up to `limit` passwords (to avoid hammering the API) and
    returns a dict of password -> breach_count (or None on failure).
    Only feasible to run against a *small* high-priority subset --
    not your entire generated wordlist.
    """
    results = {}
    for pw in passwords[:limit]:
        results[pw] = check_password(pw, timeout=timeout)
    return results
