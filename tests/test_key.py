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


def test_predict_returns_diagnostics():
    pred = kp.predict("Cmaj Gmaj Am Fmaj Cmaj")
    assert pred is not None
    assert pred.label == "C ionian"
    assert pred.n_chords == 5
    assert pred.oov_fraction == 0
    assert len(pred.scores) == kp.n_scales  # one score per reference key


def test_oov_fraction_counts_unknown_chords():
    pred = kp.predict("Cmaj Gmaj Zq")
    assert pred is not None
    assert pred.oov_fraction == pytest.approx(1 / 3)


def test_predict_empty_returns_none():
    assert kp.predict("") is None
