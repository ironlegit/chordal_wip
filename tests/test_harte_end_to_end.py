"""End-to-end acceptance test for the ChordIsolator Harte fix.

Before the fix, the all-dominant Harte song below came out of the
pipeline empty (the tab rule in _reject killed every 'root:quality'
token), so KeyPredictor.predict() returned None.  The whole pipeline
now runs all four stages, each taking and returning a space-joined
string:

    ChordIsolator.isolate -> ChordCanonizer.canonize
        -> ChordFormatter.format -> KeyPredictor.predict
"""

from chordal_wip.chordcanonizer import ChordCanonizer
from chordal_wip.chordformatter import ChordFormatter
from chordal_wip.chordisolator import ChordIsolator
from chordal_wip.key import KeyPredictor

DOMINANT_CYCLE_SONG = (
    "N G:7 F:7 E:7 Eb:7 D:7 G:7 G:7 F:7 E:7 Eb:7 D:7 G:7 "
    "G:7 F:7 E:7 Eb:7 D:7 G:7 F:7 G:7 F:7 G:7 N"
)


def test_all_dominant_cycle_yields_prediction() -> None:
    isolator = ChordIsolator()
    canonizer = ChordCanonizer()
    formatter = ChordFormatter()
    predictor = KeyPredictor()

    # Stage 1: structural validation -- only the 'N' frames may drop
    isolated = isolator.isolate(DOMINANT_CYCLE_SONG)
    assert len(isolated.split()) == 22

    # Stage 2: semantic validation -- nothing may be rejected ('X' marker)
    canonized = canonizer.canonize(isolated)
    assert len(canonized.split()) == 22
    assert canonized.split().count("X") == 0

    # Stage 3: triad reduction -- the formatter must not drop chords either
    triads = formatter.format(canonized)
    assert len(triads.split()) == 22
    # 'Eb:7' must arrive here already canonicalized to the sharp spelling
    assert "D#maj" in triads.split()

    # Stage 4: key prediction -- non-None and complete
    prediction = predictor.predict(triads)
    assert prediction is not None
    assert prediction.n_chords == 22
    # Every triad should be in the reference vocabulary; if this fails,
    # check that scales.get_ref_scales() covers all maj/m/dim roots.
    assert prediction.oov_fraction == 0.0
