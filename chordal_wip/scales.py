from typing import ValuesView
import pandas as pd
import numpy as np
import random
from chordal_wip.helpers import rotate_list


# TODO: Reconsider choice of objects for data


# TODO: Remove unicode characters and consistent use of qualities (e.g. min > m)
# TODO: Remove unicode characters and consistent use of qualities (e.g. min > m)
# TODO: Remove unicode characters and consistent use of qualities (e.g. min > m)
# TODO: Remove unicode characters and consistent use of qualities (e.g. min > m)
# TODO: Remove unicode characters and consistent use of qualities (e.g. min > m)
class Scale:
    """
    A class to represent musical scales, specifically church modes derived from the major scale.
    """

    # Class-level constants
    ALL_NOTES = np.array(
        ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    )
    # Distance between intervals in diatonic scale, i.e. 2 (whole-step) or 1 (half-step)
    DIATONIC_INTERVALS = np.array([2, 2, 1, 2, 2, 2, 1])
    SCALES_DICT = {
        "ionian": DIATONIC_INTERVALS,
        "dorian": rotate_list(DIATONIC_INTERVALS, 1),
        "phrygian": rotate_list(DIATONIC_INTERVALS, 2),
        "lydian": rotate_list(DIATONIC_INTERVALS, 3),
        "mixolydian": rotate_list(DIATONIC_INTERVALS, 4),
        "aeolian": rotate_list(DIATONIC_INTERVALS, 5),
        "locrian": rotate_list(DIATONIC_INTERVALS, 6),
    }

    def __init__(self, root_note, scale_type):
        if root_note not in self.ALL_NOTES:
            raise ValueError(
                f"Invalid root note: {root_note}. Must be one of {self.ALL_NOTES}."
            )
        if scale_type not in self.SCALES_DICT:
            raise ValueError(
                f"Invalid scale type: {scale_type}. Must be one of {list(self.SCALES_DICT.keys())}."
            )
        self.root_note = root_note
        self.scale_type = scale_type
        self.rotated_notes = self._rotate_notes()

    def _rotate_notes(self):
        """Return all notes rotated to start at the root note."""
        n_rot = np.where(Scale.ALL_NOTES == self.root_note)[0][0]
        all_notes_rot = rotate_list(Scale.ALL_NOTES, n_rot)
        return all_notes_rot

    # TODO: Use of @property is not consistent
    @property
    def notes(self):
        """Return the notes of the scale."""
        scale_dist = Scale.SCALES_DICT[self.scale_type]
        scale_indices = np.cumsum(scale_dist)[:-1]
        scale_indices_with_root = np.concatenate(([0], scale_indices))
        scale_chars = self.rotated_notes[scale_indices_with_root]
        return scale_chars

    def __str__(self):
        return (
            f"Scale:\n"
            f"  Root: {self.root_note}\n"
            f"  Scale Type: {self.scale_type}\n"
            f"  Notes: {self.notes}"
        )


# TODO: Refactor
class Chord:
    # TODO: Doesnt do anything,
    # Define chord formulas as distances from the root (in semitones)
    CHORD_FORMULAS = {
        "maj": [0, 4, 7],  # Root, major 3rd, perfect 5th
        "min": [0, 3, 7],  # Root, minor 3rd, perfect 5th
        "maj7": [0, 4, 7, 11],  # Root, major 3rd, perfect 5th, major 7th
        "min7": [0, 3, 7, 10],  # Root, minor 3rd, perfect 5th, minor 7th
        "7": [0, 4, 7, 10],  # Root, major 3rd, perfect 5th, minor 7th
        # Add more chord types as needed
    }

    # We need ionian triads and 7th chord to generate all chords for the modes using rotations
    IONIAN_BASE_CHORDS = ["maj", "m", "m", "maj", "maj", "m", "dim"]
    IONIAN_7_CHORDS = ["maj7", "min7", "min7", "maj7", "7", "min7", "min7♭5"]

    # TODO: scale_type is just needed for filtering, maybe there is a better solution
    MODE_CHORDS = pd.concat(
        [
            pd.DataFrame(
                {
                    "scale_type": ["ionian"] * 7,
                    "triads": IONIAN_BASE_CHORDS,
                    "7ths": IONIAN_7_CHORDS,
                    "roman": ["I", "ii", "iii", "IV", "V", "vi", "vii°"],
                }
            ),
            pd.DataFrame(
                {
                    "scale_type": ["dorian"] * 7,
                    "triads": rotate_list(IONIAN_BASE_CHORDS, 1),
                    "7ths": rotate_list(IONIAN_7_CHORDS, 1),
                    "roman": ["i", "ii", "♭III", "IV", "v", "vi°", "♭VII"],
                }
            ),
            pd.DataFrame(
                {
                    "scale_type": ["phrygian"] * 7,
                    "triads": rotate_list(IONIAN_BASE_CHORDS, 2),
                    "7ths": rotate_list(IONIAN_7_CHORDS, 2),
                    "roman": ["i", "♭II", "♭III", "iv", "v°", " ♭VI", "♭vii"],
                }
            ),
            pd.DataFrame(
                {
                    "scale_type": ["lydian"] * 7,
                    "triads": rotate_list(IONIAN_BASE_CHORDS, 3),
                    "7ths": rotate_list(IONIAN_7_CHORDS, 3),
                    "roman": ["I", "II", "iii", "♯iv°", "V", "vi", "vii"],
                }
            ),
            pd.DataFrame(
                {
                    "scale_type": ["mixolydian"] * 7,
                    "triads": rotate_list(IONIAN_BASE_CHORDS, 4),
                    "7ths": rotate_list(IONIAN_7_CHORDS, 4),
                    "roman": ["I", "ii", "iii°", "IV", "v", "vi", "♭VII"],
                }
            ),
            pd.DataFrame(
                {
                    "scale_type": ["aeolian"] * 7,
                    "triads": rotate_list(IONIAN_BASE_CHORDS, 5),
                    "7ths": rotate_list(IONIAN_7_CHORDS, 5),
                    "roman": ["i", "ii°", "♭III", "iv", "v", "♭VI", "♭VII"],
                }
            ),
            pd.DataFrame(
                {
                    "scale_type": ["locrian"] * 7,
                    "triads": rotate_list(IONIAN_BASE_CHORDS, 6),
                    "7ths": rotate_list(IONIAN_7_CHORDS, 6),
                    "roman": ["i°", "♭II", "♭iii", "iv", "♭V", "♭VI", "♭vii"],
                }
            ),
        ]
    )

    CHORD_DEGREES = pd.DataFrame(
        [
            {"name": "tonic", "type": "tonic", "tension": -100},
            {"name": "supertonic", "type": "subdominant", "tension": 30},
            {"name": "mediant", "type": "tonic", "tension": -80},
            {"name": "subdominant", "type": "subdominant", "tension": 20},
            {"name": "dominant", "type": "dominant", "tension": 80},
            {"name": "submediant", "type": "tonic", "tension": -70},
            {"name": "leading", "type": "dominant", "tension": 80},
        ]
    )

    def __init__(self, scale):
        # TODO: what is actually needed here?
        self.scale = scale
        self.root_note = scale.root_note
        self.scale_type = scale.scale_type
        self.notes = scale.notes
        self.data = self.merge_data()

    def merge_data(self):
        # filter df for scale_type
        mode_chords = self.MODE_CHORDS[
            self.MODE_CHORDS["scale_type"] == self.scale_type
        ].copy()

        # mutate chord cols
        mode_chords["triads"] = self.notes + mode_chords["triads"]
        mode_chords["7ths"] = self.notes + mode_chords["7ths"]

        # add chord degree information
        merged_data = pd.merge(
            mode_chords, self.CHORD_DEGREES, left_index=True, right_index=True
        )
        return merged_data

    def __str__(self):
        return (
            f"Chord:\n"
            f"  Root: {self.root_note}\n"
            f"  Scale Type: {self.scale_type}\n"
            f"  Data: {self.data}\n"
        )


class ChordProgression(Chord):
    def __init__(self, n_chords, chord: Chord):
        super().__init__(chord)  # Initialize the Chord class
        self.n_chords = n_chords
        self.progression = self.generate_chord_progression(n_chords)

    def generate_chord_progression(self, n_chords):
        # start with tonic, then subdominant, then dominant and resolve with other tonic
        tonic_chords = self.data[self.data["type"] == "tonic"]
        subdominant_chords = self.data[self.data["type"] == "subdominant"]
        dominant_chords = self.data[self.data["type"] == "dominant"]
        all_dominant_chords = self.data[
            self.data["type"].isin(["subdominant", "dominant"])
        ]

        progression = pd.DataFrame(columns=self.data.columns)
        for i in range(n_chords):
            if i == 0:
                next_chord = tonic_chords.sample(n=1)
            elif (
                i == n_chords - 1 and not progression["name"].eq("tonic").any()
            ):
                next_chord = tonic_chords[tonic_chords["name"] == "tonic"]
            elif progression["tension"].sum() <= 0:
                next_chord = all_dominant_chords.sample(n=1)
            else:
                next_chord = tonic_chords.sample(n=1)

            progression = pd.concat(
                [progression, next_chord], ignore_index=True
            )

        return progression


class MarkovChordProgression(Chord):
    def __init__(self, n_chords, chord: Chord):
        super().__init__(chord)  # init from  parent
        self.n_chords = n_chords
        self.chord_names = self.data["roman"].values
        self.intial_state = self._init_state_vec()
        self.transition_matrix = self._build_transition_matrix()
        self.progression = self.generate_progression(n_chords)
        self.tension_overall = self.progression["tension"].sum()

    def _init_state_vec(self):
        """
        Set initial state probaility vector
        """
        tension = self.data["tension"].values * -1
        tension_min_max = (tension - min(tension)) / (
            max(tension) - min(tension)
        )
        tension_norm = tension_min_max / sum(tension_min_max)
        return tension_norm

    def _build_transition_matrix(self):
        """
        Explain logic if the transition_matrix is not hardcoded anymore
        If not make it an attribute and not a method
        """

        # hardcoded transition matrix: THIS SUCKS
        transition_matrix = np.array(
            [
                # From (Row) / To (Col)
                # t   # st # m   # sd # d  # sm #ln
                [0.1, 0.2, 0.05, 0.3, 0.25, 0.1, 0.0],  #  tonic
                [0.3, 0.0, 0.1, 0.3, 0.2, 0.0, 0.1],  #  subtonic
                [0.2, 0.1, 0.0, 0.2, 0.3, 0.1, 0.1],  #  mediant
                [0.3, 0.1, 0.1, 0.1, 0.3, 0.0, 0.1],  #  Isubdominant
                [0.6, 0.0, 0.0, 0.1, 0.0, 0.2, 0.1],  #  dominant
                [0.4, 0.1, 0.1, 0.2, 0.1, 0.0, 0.1],  #  subdemiant
                [0.6, 0.0, 0.2, 0.1, 0.1, 0.0, 0.0],  #  leadning note
            ]
        )

        # Add fuzzyness depending on genre or whatevs
        return transition_matrix

    def generate_progression(self, n_chords):
        """
        Generate a chord progression using a Markov chain.

        Args:
            n_chords (int): Number of chords in the progression.

        Returns:
            pandas.DataFrame: A DataFrame containing the generated chord progression,
                             with columns for chord details (e.g., position, scale_type, triads, etc.).
                             Index is reset to a sequential range.

        Notes:
            - The first chord is selected using the initial state probability distribution (`self.initial_state`).
            - Subsequent chords are selected based on the transition probabilities from the current chord.
            - The progression is generated by sampling from the transition matrix row corresponding to the last chord.
        """
        chord_idx = list(range(0, 7))

        # Pre-allocate vec
        progression = np.empty(n_chords, dtype=int)

        # Add first chord (first state)
        progression[0] = np.random.choice(
            chord_idx, size=1, p=self.intial_state
        )

        for i in range(1, n_chords):
            last_chord_idx = progression[i - 1]
            progression[i] = np.random.choice(
                chord_idx, size=1, p=self.transition_matrix[last_chord_idx]
            )

        out = self.data.iloc[progression]
        out = out.reset_index(drop=True)

        return out


# Lazy init ----
_ref_scales = None


# TODO: decide how to handle weights
def generate_ref_scales():
    modes = ["ionian", "aeolian"]
    keys = Scale.ALL_NOTES
    chord_type = "triads"
    # Current rationale: Favor tonic to avoid introducing genre-specific bias
    weights = [2, 1, 1, 1, 1, 1, 1]

    ref_scales_list = []

    for mode in modes:
        for key in keys:
            scale_chords = Chord(Scale(key, mode)).data[chord_type].tolist()
            ref_scales_list.append(
                {
                    "key": key,
                    "mode": mode,
                    "chord_weights": {
                        chord: weight
                        for (chord, weight) in zip(scale_chords, weights)
                    },
                }
            )

    return pd.DataFrame(ref_scales_list)


def get_ref_scales():
    """
    Return the cached scales dictionary. If it hasn't been generated yet, generate it first.
    """
    global _ref_scales

    if _ref_scales is None:
        _ref_scales = generate_ref_scales()

    return _ref_scales
