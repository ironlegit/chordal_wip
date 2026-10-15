import pandas as pd
import pytest

from chordal_wip.chordpipeline import ChordProcessingPipeline
from chordal_wip.chordisolator import ChordIsolator
from chordal_wip.chordcanonizer import ChordCanonizer
from chordal_wip.chordformatter import ChordFormatter


# --- Fixtures ------------------------------------------------------------

@pytest.fixture
def pipeline():
    return ChordProcessingPipeline()


@pytest.fixture
def sample_df():
    return pd.DataFrame({"progression": ["Cmaj7, G, Am7, Fmaj7", "N Bbmaj7"]})


# --- Plumbing: the column contract --------------------------------------


def test_process_returns_new_frame_and_does_not_mutate_input(pipeline, sample_df):
    """process() must behave functionally: return a NEW frame and leave
    the caller's DataFrame untouched - like dplyr::mutate, not base-R."""
    snapshot = sample_df.copy(deep=True)

    result = pipeline.process(sample_df, "progression")

    assert result is not sample_df  # a new object, not the same frame
    assert sample_df.equals(snapshot)  # original content intact
    assert "chords_isolated" not in sample_df.columns  # no column smuggling either


def test_output_columns_and_input_are_present(pipeline, sample_df):
    result = pipeline.process(sample_df, "progression")

    # The input column survives alongside all three stage outputs.
    assert "progression" in result.columns
    assert {"chords_isolated", "chords_canonized", "chords_simplified"} <= set(
        result.columns
    )


def test_pipeline_equals_manual_stage_chain(pipeline, sample_df):
    """The composition invariant: running the pipeline must be identical
    to applying the three stages by hand, in order. If someone reorders
    or skips a step in _steps, this is the test that notices."""
    result = pipeline.process(sample_df, "progression")

    manual = (
        sample_df["progression"]
        .apply(ChordIsolator().isolate)
        .apply(ChordCanonizer().canonize)
        .apply(ChordFormatter().format)
    )

    assert result["chords_simplified"].tolist() == manual.tolist()


def test_missing_input_column_raises(pipeline):
    """Contract made loud: an unknown input column is a KeyError, not a
    silent empty result."""
    df = pd.DataFrame({"other": ["Cmaj"]})
    with pytest.raises(KeyError):
        pipeline.process(df, "progression")


def test_empty_dataframe_handled(pipeline):
    df = pd.DataFrame({"progression": pd.Series([], dtype="object")})
    result = pipeline.process(df, "progression")

    assert len(result) == 0
    assert "chords_simplified" in result.columns  # columns exist even with no rows


def test_repeated_process_is_deterministic(pipeline, sample_df):
    """Two runs over the same input must agree - guards against stage
    caches leaking state between runs (or being poisoned by them)."""
    first = pipeline.process(sample_df, "progression")["chords_simplified"]
    second = pipeline.process(sample_df, "progression")["chords_simplified"]
    assert first.tolist() == second.tolist()

# --- Pinned end-to-end anchors (regression tests) -------------------------


def test_end_to_end_simplification(pipeline):
    """A deliberately pinned expected output: this is the anchor that
    catches accidental stage regressions. If a stage change moves this
    string, that change must be a conscious decision."""
    df = pd.DataFrame({"progression": ["Cmaj7, G, Am7, Fmaj7"]})
    result = pipeline.process(df, "progression")

    assert result["chords_simplified"].iloc[0] == "Cmaj Gmaj Am Fmaj"


def test_flat_spellings_canonicalize_end_to_end(pipeline):
    """Step 8's guarantee, verified through the whole chain: a
    flat-spelled seventh chord becomes a sharp-spelled triad, identical
    to writing it sharp in the first place."""
    df = pd.DataFrame({"progression": ["Bbmaj7 A#maj7"]})
    result = pipeline.process(df, "progression")

    simplified = result["chords_simplified"].iloc[0].split()
    assert simplified[0] == simplified[1] == "A#maj"


def test_harte_no_chord_tokens_are_dropped(pipeline):
    """Harte 'N' (no chord) annotations contain no A-G letter, so the
    isolator's _erode drops them automatically - documented by test."""
    df = pd.DataFrame({"progression": ["N Cmaj7 N G N"]})
    result = pipeline.process(df, "progression")

    assert result["chords_simplified"].iloc[0] == "Cmaj Gmaj"
