from chordal_wip.key import KeyPredictor, key_relation
import pytest
import pandas as pd

kp = KeyPredictor()


# To avoid individual tests
@pytest.mark.parametrize(
    "key_a, key_b, expected",
    [
        (("C", "ionian"), ("C", "ionian"), "exact"),
        (("C", "ionian"), ("A", "aeolian"), "relative"),
        (("C", "ionian"), ("C", "aeolian"), "parallel"),
        (("C", "ionian"), ("G", "ionian"), "fifth"),
        (("C", "ionian"), ("F", "ionian"), "fifth"),
        (("C", "ionian"), ("F#", "aeolian"), "other"),
        # Tricky: a minor third apart, but same mode is NOT a relative pair
        (("C", "ionian"), ("A", "ionian"), "other"),
    ],
)
def test_key_relation(key_a, key_b, expected):
    assert key_relation(key_a[0], key_a[1], key_b[0], key_b[1]) == expected


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
    assert len(pred.probs) == kp.n_scales  # one score per reference key


def test_oov_fraction_counts_unknown_chords():
    pred = kp.predict("Cmaj Gmaj Zq")
    assert pred is not None
    assert pred.oov_fraction == pytest.approx(1 / 3)


def test_predict_empty_returns_none():
    assert kp.predict("") is None


def test_probs_sum_to_one():
    pred = kp.predict("Cmaj Gmaj Am Fmaj Cmaj")
    assert pred is not None
    assert pred.probs.sum() == pytest.approx(1.0)


def test_confidence_and_margin_ranges():
    pred = kp.predict("Cmaj Gmaj Am Fmaj Cmaj")
    assert pred is not None
    assert 0 < pred.confidence <= 1
    assert 0 <= pred.margin <= 1


def test_margin_near_zero_for_relative_tie():
    # All four chords are diatonic in BOTH C ionian and A aeolian, and
    # Cmaj/Am swap the tonic/vi roles, so the two keys score equally.
    pred = kp.predict("Cmaj Am Fmaj Gmaj")
    assert pred is not None
    assert pred.margin == pytest.approx(0.0, abs=1e-9)


def test_predict_all_basic():
    progressions = pd.Series(
        {
            "song_1": "Cmaj Gmaj Am Fmaj Cmaj Fmaj Cmaj Gmaj Cmaj",
            "song_2": "Cmaj Am Fmaj Gmaj",
            "song_3": "Xy Zq",
        }
    )
    result = kp.predict_all(progressions)

    assert len(result) == 3
    assert list(result.columns) == kp.RESULT_COLUMNS  # schema contract
    assert result["label"].iloc[0] == "C ionian"

    unusable = result[result["label"].isna()]
    assert unusable["song_id"].tolist() == ["song_3"]  # aligned with input


def test_predict_all_tie_is_consistent_with_predict():
    # The exact tie: top2_relation must be 'relative', margin ~ 0,
    # and predict_all's top-1 must agree with predict() (same tiebreak).
    tie = "Cmaj Am Fmaj Gmaj"
    result = kp.predict_all(pd.Series({"song_2": tie}))

    row = result.iloc[0]
    assert row["top2_relation"] == "relative"
    assert row["margin"] == pytest.approx(0.0, abs=1e-9)
    assert row["label"] == kp.predict(tie).label
    assert row["label_top2"] == "A aeolian"


def test_predict_all_never_reports_exact():
    progressions = pd.Series(
        {"a": "Cmaj Gmaj Am Fmaj Cmaj", "b": "Dm Dm Amaj Gmaj", "c": "Em Gmaj"}
    )
    result = kp.predict_all(progressions)
    assert (result["top2_relation"] != "exact").all()
