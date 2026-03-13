from chordal_wip.chordisolator import ChordIsolator
from re import sub

cc = ChordIsolator(char_threshold=10)


def test_tokenize():
    test = " X1 X2  X3^X4 X5%X6  (X7,X8)    X9 "

    actual = cc._tokenize(test)
    expected = ["X1", "X2", "X3", "X4", "X5", "X6", "(X7", "X8)", "X9"]

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_erode_pos():
    test = "(((((Cmaj"

    actual = cc._erode(test)
    expected = "Cmaj"

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_erode_neg():
    test = "this-is-not-a-chord"

    actual = cc._erode(test)
    expected = ""

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_reject_long():
    test = "this-is-longer-than-limit"

    actual = cc._reject(test)
    expected = True

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_reject_tab():
    test = "A|-3-2-0---x------|"

    actual = cc._reject(test)
    expected = True

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_not_reject():
    test = "Amin7(9)"

    actual = cc._reject(test)
    expected = False

    assert actual == expected, f"Expected {expected}, got {actual}"


def test_raw_chord_isolation():
    test = """
    #notchords
    Chorus
    Bridge
    #chords
    Amin
    Amaj7(13)
    Asus2dim
    A(add9)/E
    F7(9)(13)
    F#7(4)(9)
    F7(9)(5b)
    Em7sus4/B
    Fmaj7add2
    Emmaj7/Eb
    Fmaj7/11+
    C7+/9/11+
    G7/13(b9)
    Eb7(9/5-)
    D#m7(5b)
    C#madd11
    G#7M(5+)
    Cm7/b5/Bb
    D7/sus4/G
    F#m7/4(9)
    B7/9(#11)
    B7(b5/b9)
    G#madd13
    Bsus4/D#
    Ebmaj7/G
    Asus2/F#
    Gm7
    D(4)
    Csus
    Gm11
    C#7+
    Dbm6
    Gbm9
    Cm5+
    G5/F
    E13-
    Eb/9
    """

    actual = cc.raw_chord_isolation(test)
    expected = """
    Amin
    Amaj7(13)
    Asus2dim
    A(add9)/E
    F7(9)(13)
    F#7(4)(9)
    F7(9)(5b)
    Em7sus4/B
    Fmaj7add2
    Emmaj7/Eb
    Fmaj7/11+
    C7+/9/11+
    G7/13(b9)
    Eb7(9/5-)
    D#m7(5b)
    C#madd11
    G#7M(5+)
    Cm7/b5/Bb
    D7/sus4/G
    F#m7/4(9)
    B7/9(#11)
    B7(b5/b9)
    G#madd13
    Bsus4/D#
    Ebmaj7/G
    Asus2/F#
    Gm7
    D(4)
    Csus
    Gm11
    C#7+
    Dbm6
    Gbm9
    Cm5+
    G5/F
    E13-
    Eb/9
    """

    expected = expected.replace("\n", " ").strip()
    expected = sub(r"\s+", " ", expected)

    assert actual == expected, f"Expected {expected}, got {actual}"
