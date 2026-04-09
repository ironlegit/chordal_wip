import numpy as np

# import pytest
from chordal_wip.scales import Scale, Chord


def test_C_ionian_chord_generation():
    root_note = "C"
    scale_type = "ionian"
    scale = Scale(root_note, scale_type)
    chord = Chord(scale)

    # Expected triads
    expected_chords = ["Cmaj", "Dm", "Em", "Fmaj", "Gmaj", "Am", "Bdim"]
    actual_chords = list(chord.data["triads"])
    assert actual_chords == expected_chords, (
        f"Expected {expected_chords}, got {actual_chords}"
    )

    # Expected 7th chords
    expected_chords = [
        "Cmaj7",
        "Dmin7",
        "Emin7",
        "Fmaj7",
        "G7",
        "Amin7",
        "Bmin7♭5",
    ]
    actual_chords = list(chord.data["7ths"])
    assert actual_chords == expected_chords, (
        f"Expected {expected_chords}, got {actual_chords}"
    )


def test_D_dorian_chord_generation():
    root_note = "D"
    scale_type = "dorian"
    scale = Scale(root_note, scale_type)
    chord = Chord(scale)

    # Expected triads
    expected_chords = ["Dm", "Em", "Fmaj", "Gmaj", "Am", "Bdim", "Cmaj"]
    actual_chords = list(chord.data["triads"])
    assert actual_chords == expected_chords, (
        f"Expected {expected_chords}, got {actual_chords}"
    )

    # Expected 7th chords
    expected_chords = [
        "Dmin7",
        "Emin7",
        "Fmaj7",
        "G7",
        "Amin7",
        "Bmin7♭5",
        "Cmaj7",
    ]
    actual_chords = list(chord.data["7ths"])
    assert actual_chords == expected_chords, (
        f"Expected {expected_chords}, got {actual_chords}"
    )


def test_F_myxolydian_chord_generation():
    root_note = "F#"
    scale_type = "mixolydian"
    scale = Scale(root_note, scale_type)
    chord = Chord(scale)

    # Expected triads
    expected_chords = [
        "F#maj",
        "G#m",
        "A#dim",
        "Bmaj",
        "C#m",
        "D#m",
        "Emaj",
    ]
    actual_chords = list(chord.data["triads"])
    assert actual_chords == expected_chords, (
        f"Expected {expected_chords}, got {actual_chords}"
    )

    # Expected 7th chords
    expected_chords = [
        "F#7",
        "G#min7",
        "A#min7♭5",
        "Bmaj7",
        "C#min7",
        "D#min7",
        "Emaj7",
    ]
    actual_chords = list(chord.data["7ths"])
    assert actual_chords == expected_chords, (
        f"Expected {expected_chords}, got {actual_chords}"
    )
