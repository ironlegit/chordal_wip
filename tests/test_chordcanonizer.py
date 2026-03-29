from chordal_wip.chordcanonizer import ChordCanonizer
import pytest

cc = ChordCanonizer()


def test_decompose():
    test = "Ebmaj7add9/G"

    actual = cc._decompose(test)

    expected = {
        "root": "Eb",
        "quality": "maj",
        "quality_5th": None,
        "quality_7th": None,
        "adds": ["add9"],
        "extensions": ["7"],
        "no": None,
        "slash": "G",
        "unclear": [],
    }
    assert actual == expected, f"Expected {expected}, got {actual}"


def test_normalize():
    test = "Ebmaj7add9/G"

    decomp = cc._decompose(test)
    actual = cc._normalize(decomp)

    expected = {
        "root": "Eb",
        "quality": "maj",
        "quality_5th": None,
        "quality_7th": "maj",
        "adds": ["add9"],
        "extensions": [],
        "no": None,
        "slash": "G",
        "unclear": [],
    }
    assert actual == expected, f"Expected {expected}, got {actual}"


def test_num_sort():
    test = ["add9", "add2", "add13", "X"]

    actual = [cc._num_sort(i) for i in test]
    expected = [9, 2, 13, 999]

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_length_conservation():
    test = "not_chord exit progression lit effect"

    actual = cc.canonize(test)
    expected = "X X X X X"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_triads_1():
    test = "Emin Em E- EMaj Emaj EM"

    actual = cc.canonize(test)
    expected = "E(q3:m) E(q3:m) E(q3:m) E(q3:maj) E(q3:maj) E(q3:maj)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_triads_2():
    test = "E G# Cb/Db"

    actual = cc.canonize(test)
    expected = "E(q3:maj) G#(q3:maj) Cb(q3:maj)/Db"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_ext_migration_to_adds():
    # 2 and 4 should migrate to adds, triggering major triad detection
    test = "C2 C4 Cm2"

    actual = cc.canonize(test)
    expected = "C(q3:maj)(m:add2) C(q3:maj)(m:add4) C(q3:m)(m:add2)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_adds():
    # add with accidental, and dedup when add and extension overlap
    test = "Cadd#11 Cmaj9add9"

    actual = cc.canonize(test)
    expected = "C(q3:maj)(m:add#11) C(q3:maj)(q7:maj)(e:9)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_aug_1():
    test = "C5+ C+5 Caug C+"

    actual = cc.canonize(test)
    expected = "C(q3:maj)(q5:aug) C(q3:maj)(q5:aug) C(q3:maj)(q5:aug) C(q3:maj)(q5:aug)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_aug_2():
    test = "C7+ Caug7 C7+/9"

    actual = cc.canonize(test)
    expected = "C(q3:maj)(q5:aug)(q7:m) C(q3:maj)(q5:aug)(q7:m) C(q3:maj)(q5:aug)(q7:m)(e:9)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_aug_3():
    test = "C+M7 Cmaj7/#5"

    actual = cc.canonize(test)
    expected = "C(q3:maj)(q5:aug)(q7:maj) C(q3:maj)(q5:aug)(q7:maj)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_aug_trailing_plus_non_seven():
    # "C9+" → augmented with 9th
    test = "C9+"

    actual = cc.canonize(test)
    expected = "C(q3:maj)(q5:aug)(q7:m)(e:9)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_sus():
    test = "Csus Csus2 Csus4 Csus9 Csus/E"

    actual = cc.canonize(test)
    expected = (
        "C(q3:sus4) C(q3:sus2) C(q3:sus4) C(q3:sus4)(q7:m)(e:9) C(q3:sus4)/E"
    )

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_dim():
    test = "Cdim D#dim7 Dbdim Cdim/Ab"

    actual = cc.canonize(test)
    expected = "C(q5:dim) D#(q5:dim)(q7:dim) Db(q5:dim) C(q5:dim)/Ab"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_half_diminished():
    # Cm7b5 is the half-diminished chord, distinct from full dim7
    test = "Cm7b5 Cmin7b5 F#/-7b5"

    actual = cc.canonize(test)
    expected = (
        "C(q3:m)(q5:dim)(q7:m) C(q3:m)(q5:dim)(q7:m) F#(q3:m)(q5:dim)(q7:m)"
    )

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_slash():
    test = "E#/Cb E#7/9/Cb C/D Ebsus4(7)/C#"

    actual = cc.canonize(test)
    expected = "E#(q3:maj)/Cb E#(q3:maj)(q7:m)(e:9)/Cb C(q3:maj)/D Eb(q3:sus4)(q7:m)/C#"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_sixth():
    # C6 has no 7th — extension 6 should not trigger has_seventh logic
    # C6/9 is a common jazz voicing also without a 7th — worth verifying
    # your parser's stance on this explicitly
    test = "C6 C6/9"

    actual = cc.canonize(test)
    expected = (
        "C(q3:maj)(e:6) C(q3:maj)(e:6,9)"  # no q7 — verify this is intentional
    )

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_7th():
    test = "Emaj7 Emin7 Em7 E7M EM7 E7"

    actual = cc.canonize(test)
    expected = "E(q3:maj)(q7:maj) E(q3:m)(q7:m) E(q3:m)(q7:m) E(q3:maj)(q7:maj) E(q3:maj)(q7:maj) E(q3:maj)(q7:m)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_7th_2():
    test = "Gmaj9 Gmaj7 Gmaj7(9+) G9"

    actual = cc.canonize(test)
    expected = "G(q3:maj)(q7:maj)(e:9) G(q3:maj)(q7:maj) G(q3:maj)(q7:maj)(e:#9) G(q3:maj)(q7:m)(e:9)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_7th_3():
    test = "Gmmaj7 Gmmaj11"

    actual = cc.canonize(test)
    expected = "G(q3:m)(q7:maj) G(q3:m)(q7:maj)(e:11)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_trailing_minus_with_explicit_quality():
    # maj already stated → 9- means b9, not minor
    test = "Cmaj9- C7+/9/E"

    actual = cc.canonize(test)
    expected = "C(q3:maj)(q7:maj)(e:b9) C(q3:maj)(q5:aug)(q7:m)(e:9)/E"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_minor_trailing_dash():
    # "E13-" → minor 13, not Eb13
    test = "E13- Em13"

    actual = cc.canonize(test)
    expected = "E(q3:m)(q7:m)(e:13) E(q3:m)(q7:m)(e:13)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_no_extensions():
    test = "G#(no3rd) G(no5th) D11(no7)"

    actual = cc.canonize(test)
    expected = "G#(n:no3) G(q3:maj)(n:no5) D(q3:maj)(e:11)(n:no7)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_weird():
    test = "Em777 E7add7"

    actual = cc.canonize(test)
    expected = "E(q3:m)(q7:m) E(q3:maj)(q7:m)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_extensions():
    test = "C7/9- C9#11b13 C911+13-"

    actual = cc.canonize(test)
    expected = "C(q3:maj)(q7:m)(e:b9) C(q3:maj)(q7:m)(e:9,#11,b13) C(q3:maj)(q7:m)(e:9,#11,b13)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonize_wrong_canonizations():
    """
    Leading accidentals "+" and "-" are not allowed.
    Trailing accidentals "#" and "b" are not allowed.
    Cave: Two trailing accidentals using "#" and "b" are wronly interpreted as valid cases, because of the above rules!
    """
    test = "F7(9b) C7/-9 C7/9b C7/9# C911#13b"

    actual = cc.canonize(test)
    expected_list = [
        "F(q3:maj)(q7:m)(e:9)",  # "7(9b)" becomes "79b" and is tokenzied as "7" and "9", trailing b is dropped
        "C(q3:maj)(q7:m)(e:9)",  # "7/-9" becomes "7-9" and is tokenized as "7-" and "9"
        "C(q3:maj)(q7:m)(e:9)",  # Same as first example
        "C(q3:maj)(q7:m)(e:9)",  # Same as first example with sharp
        "C(q3:maj)(q7:m)(e:9,11,#13)",  # Trailing # or b are not expected, hence it favors #13 instead of 11# and 13b.
    ]
    expected = " ".join(expected_list)

    assert actual == expected, f"Expected {expected}, got {actual}"
