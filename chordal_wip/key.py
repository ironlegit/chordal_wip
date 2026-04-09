from pytest import approx
import chordal_wip.scales as scales
import pandas as pd


class KeyPredictor:
    """
    A class for predicting key from a chord progression.
    """

    def __init__(self):  # , reference: pd.DataFrame):
        self.reference = scales.get_ref_scales()
        self.weights_df = pd.DataFrame.from_records(
            self.reference["chord_weights"]
        )

    # Public methods
    def predict_key(self, chords: str) -> str:
        # TODO: The chords itself will also come as a Panda Series
        chords = pd.Series(chords.split(" "))
        n_chords = len(chords)

        # TODO: What to do with slash chords?
        # [chord for chord in chord_lst if "/" not in chord]
        counts = chords.value_counts(ascending=False)

        # Stats
        proportions = counts / n_chords

        self._integrity_proportions(proportions)

        # Creates a weight-matrix of all scales (rows) and all chords (cols)
        scores = (self.weights_df.mul(proportions, axis=1)).sum(axis=1)

        # TODO: this is a bit confusing...
        ref = self.reference
        ref["scores"] = scores.values
        key_mode = self.reference.loc[scores.idxmax(), ["key", "mode"]]

        return f"{key_mode['key']} {key_mode['mode']}"

    # Private methods
    # TODO: RM once slash handling is clear!
    def _integrity_proportions(self, proportions: pd.Series):
        sum_to_one = proportions.sum()

        if sum_to_one != approx(1.0):
            raise ValueError(f"Proportions do not sum to 1, got {sum_to_one}")

    def __str__(self):
        return (
            f"Chord Progression:\n{self.chord_proportions}\n"
            f"Best Matching Scale: {self.top_scale['key']} {self.top_scale['mode']}"
        )


# progression = "Cmaj Gmaj Am Fmaj Cmaj Fmaj Cmaj Fmaj Cmaj Gmaj Am Fmaj"
# kp2 = KeyPredictor()
# x = kp2.predict_key(progression)
# print(x)
