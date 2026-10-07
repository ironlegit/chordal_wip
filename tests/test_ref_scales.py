from chordal_wip import scales
from chordal_wip.key import KeyPredictor


def test_ref_scales_is_cached():
    # 'is' checks OBJECT IDENTITY (same object in memory), '==' checks
    # equality of values. For a cache, identity is the whole point.
    assert scales.get_ref_scales() is scales.get_ref_scales()


def test_ref_scales_shape():
    ref = scales.get_ref_scales()
    assert len(ref) == 24  # 12 tonics x 2 modes
    assert set(ref["mode"]) == {"ionian", "aeolian"}
    assert set(ref.columns) == {"key", "mode", "chord_weights"}


def test_key_predictor_accepts_custom_reference():
    # The injection point for the benchmark's profile sweep.
    ref = scales.get_ref_scales().copy()  # .copy(): respect the read-only contract
    pred = KeyPredictor(reference=ref)
    assert pred.predict_key("Cmaj Gmaj Am Fmaj Cmaj") == "C ionian"
