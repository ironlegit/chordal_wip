from collections import Counter
from pytest import approx
from chordal_wip.helpers import rotate_list
import chordal_wip.scales as scales
import pandas as pd


class KeyPredictor:
    """
    A class for predicting key from a chord progression.
    """

    def __init__(self, chord_txt: str, reference: pd.DataFrame):
        self.chord_txt = chord_txt
        self.chord_progression = self._chord_progression()
        self.n_chords = len(self.chord_progression)
        self.chord_counts = self._count_chords()
        self.chord_proportions = self._chord_proportions()
        self._integrity_proportions()
        self.reference = reference
        self.scores = self._calculate_scores()
        self.top_scale = self.reference.loc[
            self.scores.idxmax(), ["key", "mode"]
        ]

    def _chord_progression(self) -> list:
        chord_lst = self.chord_txt.split(" ")
        return [chord for chord in chord_lst if "/" not in chord]

    def _count_chords(self) -> pd.Series:
        counts_unsorted = pd.Series(Counter(self.chord_progression))
        return self._sort_chords(counts_unsorted)

    def _chord_proportions(self) -> pd.Series:
        return self.chord_counts / self.n_chords

    def _integrity_proportions(self):
        sum_to_one = self.chord_proportions.sum()

        if sum_to_one != approx(1.0):
            raise ValueError(f"Proportions do not sum to 1, got {sum_to_one}")

    def _sort_chords(self, counts_unsorted: pd.Series) -> pd.Series:
        # Find key with highest value
        max_key = counts_unsorted.idxmax()

        # Get sorted index as a list
        sorted_index = counts_unsorted.sort_index().index.tolist()

        # Find position of max_key
        max_key_idx = sorted_index.index(max_key)

        # Rotate the index list
        rotated_index = rotate_list(sorted_index, max_key_idx, dir="left")

        return counts_unsorted[rotated_index]

    def _calculate_scores(self) -> pd.Series:
        """Vectorized calculation of scores for all scales in reference."""

        # Creates a weight-matrix of all scales (rows) and all chords (cols)
        weights_df = pd.DataFrame.from_records(self.reference["chord_weights"])

        # Multiply the chord freqs (progression) with the weights of the references
        scores = (weights_df.mul(self.chord_proportions, axis=1)).sum(axis=1)
        ref = self.reference
        ref["scores"] = scores.values
        print(ref)
        return scores

    def __str__(self):
        return (
            f"Chord Progression:\n{self.chord_proportions}\n"
            f"Best Matching Scale: {self.top_scale['key']} {self.top_scale['mode']}"
        )


# TODO: Main issue is that it is not yet clear what kind of chord format should be used here.
# progression = "Dm Dm A7 G7 Dm Dm A7 G7 Bm A G A Dm Dm A7 G7 Bm A G A Dm Dm A7 G7 Bm A G A Dm"
#
# # progression = "Cmaj Gmaj Am Fmaj Cmaj Fmaj Cmaj Fmaj Cmaj Gmaj Am Fmaj"
# reference = scales.get_ref_scales()
# kp = KeyPredictor(progression, reference)
#
# print(kp)
# exit()
# actual_key = f"{kp['key']} {kp['mode']}"
# print(f"actual_key : {actual_key}")
# expected_key = "C ionian"
# print(f"expected_key : {expected_key}")
#
# print(actual_key == expected_key)
