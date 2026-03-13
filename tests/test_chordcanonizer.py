from chordal_wip.chordcanonizer import ChordCanonizer
import pytest

cc = ChordCanonizer()


def test_decompose_1():
    test = "Ebmaj7add9/G"

    actual = cc._decompose(test)
    expected = {
        "root": "Eb",
        "quality": "maj",
        "adds": ["add9"],
        "sus": None,
        "dominant": None,
        "extensions": ["7"],
        "alterations": [],
        "slash": "G",
        "unclear": [],
    }
    assert actual == expected, f"Expected {expected}, got {actual}"


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
    expected = "E(q:m) E(q:m) E(q:m) E(q:maj) E(q:maj) E(q:maj)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonicalize_aug():
    test = "C5+ C+5 C7+ Caug C+"

    actual = cc.canonicalize(test)
    expected = "C(a:#5) C(e:5)(a:#5) C(d:True)(e:7)(a:#5) C(a:#5) C(a:#5)"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonicalize_sus():
    test = "Csus Csus2 Csus4 Csus9 Csus/E"

    actual = cc.canonicalize(test)
    expected = (
        "C(s:sus4) C(s:sus2) C(s:sus4) C(s:sus4)(d:True)(e:9) C(s:sus4)/E"
    )

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_canonicalize_dim():
    test = "Cdim D#dim7 Dbdim Cdim/Ab"

    actual = cc.canonicalize(test)
    expected = "C(q:dim) D#(q:dim)(e:7) Db(q:dim) C(q:dim)/Ab"

    assert actual == expected, f"Expected {expected}, got {actual}"


@pytest.mark.skip("Figure out dominant issue!!")
def test_canonicalize_slash():
    test = "E#/Cb E#7/9/Cb C/D Ebsus4(7)/C#"

    actual = cc.canonicalize(test)
    expected = "E#(q:maj)/Cb E#(d:True)(e:7,9)/Cb C(q:maj)/D Eb(s:sus4)(e:7)/C#"

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
