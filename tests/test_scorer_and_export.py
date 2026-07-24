import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pwlgen import scorer, hashcat_export


def test_charset_size_lowercase_only():
    assert scorer.charset_size("tiger") == 26


def test_charset_size_mixed():
    size = scorer.charset_size("Tiger1!")
    assert size == 26 + 26 + 10 + 32


def test_shannon_entropy_increases_with_length():
    e1 = scorer.shannon_entropy_bits("tiger")
    e2 = scorer.shannon_entropy_bits("tigertiger")
    assert e2 > e1


def test_guessability_prefers_profile_word_prefix():
    score_match = scorer.guessability_score("tiger123", ["tiger"])
    score_nomatch = scorer.guessability_score("xk9plq123", ["tiger"])
    assert score_match < score_nomatch


def test_rank_candidates_sorted_ascending():
    candidates = ["tiger123", "T!g3r@#$999xyz", "tiger"]
    ranked = scorer.rank_candidates(candidates, ["tiger"])
    scores = [s for _, s, _ in ranked]
    assert scores == sorted(scores)


def test_rank_candidates_top_n_limits_output():
    candidates = ["a1", "b2", "c3", "d4", "e5"]
    ranked = scorer.rank_candidates(candidates, [], top_n=2)
    assert len(ranked) == 2


def test_hashcat_rule_generation_nonempty():
    lines = hashcat_export.generate_rule_lines()
    assert len(lines) > 0
    assert "" in lines  # no-op rule present
    assert "l" in lines
    assert "u" in lines
