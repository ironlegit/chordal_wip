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
        "dominant": None,
        "extensions": ["7"],
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
        "dominant": None,
        "extensions": [],
        "slash": "G",
        "unclear": [],
    }
    assert actual == expected, f"Expected {expected}, got {actual}"


@pytest.mark.skip(reason="rethink edge case handling!")
def test_edge_cases_1():
    test = "E13-"

    actual = cc.canonicalize(test)
    expected = "Em13"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_num_sort():
    test = ["add9", "add2", "add13", "X"]

    actual = [cc._num_sort(i) for i in test]
    expected = [9, 2, 13, 999]

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonicalize_length_conservation():
    test = "not_chord exit progression lit effect"

    actual = cc.canonicalize(test)
    expected = "X X X X X"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonicalize_triads():
    test = "Emin Em E- EMaj Emaj EM"

    actual = cc.canonicalize(test)
    expected = "E(q3:m) E(q3:m) E(q3:m) E(q3:maj) E(q3:maj) E(q3:maj)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonicalize_aug_1():
    test = "C5+ C+5 Caug C+"

    actual = cc.canonicalize(test)
    expected = "C(q3:maj)(q5:aug) C(q3:maj)(q5:aug) C(q3:maj)(q5:aug) C(q3:maj)(q5:aug)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonicalize_aug_2():
    test = "C7+ Caug7 C7+/9"

    actual = cc.canonicalize(test)
    expected = "C(q3:maj)(q5:aug)(q7:m) C(q3:maj)(q5:aug)(q7:m) C(q3:maj)(q5:aug)(q7:m)(e:9)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonicalize_aug_3():
    test = "C+M7 Cmaj7/#5"

    actual = cc.canonicalize(test)
    expected = "C(q3:maj)(q5:aug)(q7:maj) C(q3:maj)(q5:aug)(q7:maj)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonicalize_sus():
    test = "Csus Csus2 Csus4 Csus9 Csus/E"

    actual = cc.canonicalize(test)
    expected = (
        "C(q3:sus4) C(q3:sus2) C(q3:sus4) C(q3:sus4)(q7:m)(e:9) C(q3:sus4)/E"
    )

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonicalize_dim():
    test = "Cdim D#dim7 Dbdim Cdim/Ab"

    actual = cc.canonicalize(test)
    expected = "C(q5:dim) D#(q5:dim)(q7:dim) Db(q5:dim) C(q5:dim)/Ab"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonicalize_slash():
    test = "E#/Cb E#7/9/Cb C/D Ebsus4(7)/C#"

    actual = cc.canonicalize(test)
    expected = "E#(q3:maj)/Cb E#(q3:maj)(q7:m)(e:9)/Cb C(q3:maj)/D Eb(q3:sus4)(q7:m)/C#"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonicalize_7th():
    test = "Emaj7 Emin7 Em7 E7M EM7 E7"

    actual = cc.canonicalize(test)
    expected = "E(q:maj)(e:7) E(q:m)(e:7) E(q:m)(e:7) E(q:maj)(e:7) E(q:maj)(e:7) E(d:True)(e:7)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonicalize_7th_2():
    test = "Gmaj9 Gmaj7 Gmaj7(9+) G9"

    actual = cc.canonicalize(test)
    expected = "G(q:maj)(e:9) G(q:maj)(e:7) G(q:maj)(e:7,#9) G(d:True)(e:9)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonicalize_weird():
    test = "Em777 E7add7"

    actual = cc.canonicalize(test)
    expected = "E(q:m)(e:7) E(d:True)(e:7)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonicalize_extensions():
    test = "C7/9- C9#11b13 C911+13-"

    actual = cc.canonicalize(test)
    expected = "C(d:True)(e:7,b9) C(d:True)(e:9,#11,b13) C(d:True)(e:9,#11,b13)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonicalize_extensions_edge_cases():
    """
    Leading accidentals "+" and "-" are not allowed.
    Trailing accidentals "#" and "b" are not allowed.
    Cave: Two trailing accidentals using "#" and "b" are wronly interpreted as valid cases, because of the above rules!
    """
    test = "C7/-9 C7/9b C7/9# C911#13b"

    actual = cc.canonicalize(test)
    expected_list = [
        "C(d:True)(e:7)(u:-9)",  # Leading "-" is not expected in token splitting criteria
        "C(d:True)(e:7,b9)",  # Correctly interpreted because of slash handling
        "C(d:True)(e:7,#9)",  # Same as above
        "C(d:True)(e:9,11,#13)",  # Trailing # or b are not expected, hence it favors #13 instead of 11# and 13b.
    ]
    expected = " ".join(expected_list)

    assert actual == expected, f"Expected {expected}, got {actual}"
