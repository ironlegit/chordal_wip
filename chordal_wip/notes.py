"""chordal_wip/notes.py - single source of truth for pitch-class naming."""

import numpy as np

# One canonical spelling per pitch class: sharps. Lossless in 12-TET.
FLAT_TO_SHARP = {
    "Bb": "A#",
    "Eb": "D#",
    "Ab": "G#",
    "Db": "C#",
    "Gb": "F#",
    "Cb": "B",
    "Fb": "E",
}

# TODO: RM everywhere else
ALL_NOTES = np.array(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])

# Map note names to pitch classes (C=0, C#=1, ..., B=11).
# This is used to measure distance between keys and note names
NOTE_TO_PITCH_CLASS = {note: pc for pc, note in enumerate(ALL_NOTES.tolist())}
