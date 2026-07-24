import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pwlgen import generator


def test_leet_variants_includes_original():
    variants = generator.leet_variants("tiger")
    assert "tiger" in variants


def test_leet_variants_produces_substitutions():
    variants = generator.leet_variants("tiger")
    assert any("7" in v or "!" in v or "1" in v for v in variants)


def test_leet_variants_no_eligible_chars_returns_word_only():
    variants = generator.leet_variants("xyz")
    assert variants == {"xyz"}


def test_case_variants():
    variants = generator.case_variants("tiger")
    assert "tiger" in variants
    assert "Tiger" in variants
    assert "TIGER" in variants


def test_date_tokens_full_date():
    tokens = generator.date_tokens("15081999")
    assert "1999" in tokens
    assert "99" in tokens
    assert "1508" in tokens or "0815" in tokens


def test_date_tokens_year_only():
    tokens = generator.date_tokens("1999")
    assert "1999" in tokens
    assert "99" in tokens


def test_keyboard_walk_variants_splices_word():
    variants = generator.keyboard_walk_variants("tiger")
    assert any(v.startswith("tiger") for v in variants)
    assert any(v.endswith("tiger") for v in variants)


def test_build_wordlist_respects_length_bounds():
    profile = {"name": "Rajesh", "surname": "Kumar", "dob": "15081999"}
    result = generator.build_wordlist(profile, min_len=6, max_len=10)
    assert all(6 <= len(w) <= 10 for w in result)


def test_build_wordlist_nonempty_for_valid_profile():
    profile = {"name": "Rajesh", "dob": "15081999"}
    result = generator.build_wordlist(profile)
    assert len(result) > 0


def test_build_wordlist_includes_profile_derived_candidate():
    profile = {"name": "Tiger"}
    result = generator.build_wordlist(profile, include_keyboard_walks=False)
    assert any(w.lower().startswith("tiger") for w in result)
