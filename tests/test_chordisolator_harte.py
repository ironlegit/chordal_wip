"""Regression tests: Harte-qualified chord tokens must survive ChordIsolator.

Context: the tab rule in ``_reject`` used to include ':' in its character
class, so every Harte token from the Isophonics datasets ('G:7', 'A:min', ...)
was silently rejected before it ever reached the canonizer.

Grammar reference: Harte, Sandler, Abdallah & Gomez (2005), "Symbolic
representation of musical chords: a proposed syntax for text annotations",
ISMIR -- Table 1 (BNF) and Table 2 (shorthand vocabulary).
"""

from collections import Counter

import pytest

from chordal_wip.chordisolator import ChordIsolator

# The benchmark song that used to come out empty: 22 dominant sevenths,
# framed by 'N' (no-chord) tokens.
DOMINANT_CYCLE_SONG = (
    "N G:7 F:7 E:7 Eb:7 D:7 G:7 G:7 F:7 E:7 Eb:7 D:7 G:7 "
    "G:7 F:7 E:7 Eb:7 D:7 G:7 F:7 G:7 F:7 G:7 N"
)

# A guitar-tab listing from the main dataset: every fragment here is junk
# that must keep dying after the Harte fix.  Only the trailing bare 'G'
# (a genuine chord closing the line) survives.
TAB_LISTING = (
    "G: 320033 D/F#: 2x0232 Em: 022000 Bm7: x24232 C: x32010 "
    "G/B: x20033 Am7: x02010 D11: xx0010 G"
)


@pytest.fixture
def isolator() -> ChordIsolator:
    return ChordIsolator()


# --- Harte tokens survive isolation ---------------------------------------


@pytest.mark.parametrize(
    "token",
    [
        "G:7",  # dominant seventh (the all-:7 benchmark song)
        "A:min",  # plain minor
        "C:maj",  # plain major
        "Bb:sus2",  # flat root: spelling preserved at isolator level
        # (canonicalized to A# downstream, not tested here)
        "Eb:7",  # flat root dominant (-> D# downstream)
        "F#:min7",  # sharp root + minor seventh
        "C:maj7",  # major seventh
        "B:dim7",  # diminished seventh shorthand
        "E:aug",  # augmented
        "D:hdim7",  # half-diminished: official Harte shorthand (Table 2)
        "A:minmaj7",  # minor-major seventh: official Harte shorthand
        "C:sus4",  # suspended fourth
        "C:maj6",  # major sixth
        "C:9",  # bare digit shorthand (dominant ninth)
        "A:maj/3",  # Harte inversion: bass is a DEGREE, not a note
        "C:min/b3",  # inversion with a flattened degree
        "C:maj(4)",  # shorthand plus degree list (no comma)
    ],
)
def test_harte_token_survives(isolator: ChordIsolator, token: str) -> None:
    """Token passes structural validation unchanged."""
    assert isolator.isolate(token) == token


# --- Colon junk from the main dataset still dies --------------------------


@pytest.mark.parametrize(
    "token",
    [
        "G:",  # tab listing: root + colon, nothing after it
        "C:",  # same
        "Am:",  # colon NOT directly after the root -> fails anatomy
        "Bm7:",  # same
        "Em:",  # same
        "D11:",  # same
        "D/F#:",  # trailing colon after a slash bass
        "C:x32010",  # fret digits glued after the colon
    ],
)
def test_colon_junk_still_dies(isolator: ChordIsolator, token: str) -> None:
    """Only a real Harte quality/degree after ':' survives."""
    assert isolator.isolate(token) == ""


# --- Non-colon tab protections unchanged ----------------------------------


@pytest.mark.parametrize(
    "token",
    [
        "A|",  # root + pipe
        "G7-E7-B7-E7",  # coagulated string (>2 roots)
        "G7/E7/B7/E7",  # coagulated string (>2 roots)
        "E022100",  # strum digits glued to a root
    ],
)
def test_tab_junk_still_dies(isolator: ChordIsolator, token: str) -> None:
    assert isolator.isolate(token) == ""


def test_full_tab_listing_still_dies(isolator: ChordIsolator) -> None:
    """The whole tab listing reduces to the one genuine chord in it."""
    assert isolator.isolate(TAB_LISTING) == "G"


def test_root_dash_pair_is_split_not_rejected(isolator: ChordIsolator) -> None:
    """'E -' is never a single token: _tokenize splits on whitespace.

    The bare root 'E' is a legitimate (major) chord and survives; only
    '-' is dropped.  This is pre-existing behaviour, unchanged by the fix:
    the '\\s' in the tab character class could never match inside a token
    anyway, because tokens are whitespace-split beforehand.
    """
    assert isolator.isolate("E -") == "E"


# --- Main-dataset behaviours must not regress ------------------------------


def test_section_marker_prefix_still_dies(isolator: ChordIsolator) -> None:
    """'Intro:' dies in _erode (no A-G before the colon); chords survive."""
    assert isolator.isolate("Intro: B C#m7") == "B C#m7"


def test_production_format_unchanged(isolator: ChordIsolator) -> None:
    assert isolator.isolate("A Bmaj C Dmin7") == "A Bmaj C Dmin7"


def test_comma_coagulation_split_unchanged(isolator: ChordIsolator) -> None:
    """Special-token separator still splits 'G7,E7' inside tokens."""
    assert isolator.isolate("G7,E7") == "G7 E7"


@pytest.mark.parametrize("token", ["N", "(N)"])
def test_no_chord_token_dropped(isolator: ChordIsolator, token: str) -> None:
    """Harte no-chord marker dies in _erode (no uppercase A-G)."""
    assert isolator.isolate(token) == ""


# --- The benchmark song -----------------------------------------------------


def test_all_dominant_cycle_survives_isolation(
    isolator: ChordIsolator,
) -> None:
    """The all-:7 song keeps all 22 dominants; only the 'N' frames drop."""
    out = isolator.isolate(DOMINANT_CYCLE_SONG).split()
    assert len(out) == 22
    assert all(tok.endswith(":7") for tok in out)


# --- Token-count reconciliation ---------------------------------------------


def reconcile_tokens(
    txt: str, isolator: ChordIsolator
) -> dict[str, int | dict[str, int]]:
    """Compare raw token count to isolated chord count and list the drops.

    Run this over a whole .lab file (or a whole dataset) after re-running
    the benchmark: the expected gap between n_raw and n_kept is exactly
    the 'N' tokens plus genuine junk -- anything else deserves a look.

    Caveat: kept tokens are the post-erode/_homogenize strings, so a token
    that survives only after cleaning (e.g. 'Cmaj7°') shows up in
    'dropped' as well; that is fine for eyeballing, not for strict asserts.
    """
    raw = isolator._tokenize(txt)
    kept = isolator.isolate(txt).split()
    dropped = Counter(raw) - Counter(kept)
    return {"n_raw": len(raw), "n_kept": len(kept), "dropped": dict(dropped)}


def test_reconciliation_dominant_cycle(isolator: ChordIsolator) -> None:
    """For the all-:7 song the only gap must be the two 'N' tokens."""
    report = reconcile_tokens(DOMINANT_CYCLE_SONG, isolator)
    assert report["n_raw"] == 24
    assert report["n_kept"] == 22
    assert report["dropped"] == {"N": 2}


def test_reconciliation_tab_listing(isolator: ChordIsolator) -> None:
    """For tab listings the drop set is the tab junk itself."""
    report = reconcile_tokens(TAB_LISTING, isolator)
    assert report["n_kept"] == 1
    assert report["dropped"]["G:"] == 1  # 'G:'-style fragments die in _reject
