from chordal_wip.key import KeyPredictor

import pytest

kp = KeyPredictor()


def test_C_ionian_key_prediction():
    progression = "Cmaj Gmaj Am Fmaj Cmaj Fmaj Cmaj Fmaj Cmaj Gmaj Am Fmaj"

    actual_key = kp.predict_key(progression)
    expected_key = "C ionian"
    assert actual_key == expected_key, f"Expected {expected_key}, got {actual_key}"


def test_come_together_beatles_key_prediction():
    progression = "Dm Dm Amaj Gmaj Dm Dm Amaj Gmaj Bm Amaj Gmaj Amaj Dm Dm Amaj Gmaj Bm Amaj Gmaj Amaj Dm Dm Amaj Gmaj Bm Amaj Gmaj Amaj Dm"

    actual_key = kp.predict_key(progression)
    expected_key = "A ionian"  # OR "D aeolian"?
    assert actual_key == expected_key, f"Expected {expected_key}, got {actual_key}"


def test_only_unknown_chords_returns_none():
    # Nothing here is a valid chord: the predictor must refuse
    # instead of silently returning reference row 0.
    assert kp.predict_key("Xy Zq Xy") is None
