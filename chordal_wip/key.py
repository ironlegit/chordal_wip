from pytest import approx
import chordal_wip.scales as scales
import pandas as pd


# TODO: This is very slow
# TODO: This is very slow
# TODO: This is very slow
# TODO: This is very slow
# TODO: This is very slow
# TODO: This is very slow
class KeyPredictor:
    """
    A class for predicting key from a chord progression.
    """

    def __init__(self):  # , reference: pd.DataFrame):
        self.reference = scales.get_ref_scales()
        # Weight-matrix of all scales (rows) and all chords (cols)
        self.weights_df = pd.DataFrame.from_records(
            self.reference["chord_weights"]
        )

    # Public methods
    def predict_key(self, chords: str) -> str:
        # TODO: The chords itself will also come as a Panda Series
        chords = pd.Series(chords.split(" "))
        # [chord for chord in chord_lst if "/" not in chord]

        n_chords = len(chords)
        counts = chords.value_counts(ascending=False)
        proportions = counts / n_chords

        self._integrity_proportions(proportions)

        # Multiply chord proportions by weights of all scales (only matching chords)
        scores = (self.weights_df.mul(proportions, axis=1)).sum(axis=1)

        # TODO: What about ties?
        max_score_idx = scores.idxmax()
        ref_max = self.reference.loc[max_score_idx, ["key", "mode"]]
        return f"{ref_max['key']} {ref_max['mode']}"

    # Private methods
    # TODO: RM once slash handling is clear!
    def _integrity_proportions(self, proportions: pd.Series):
        sum_to_one = proportions.sum()

        if sum_to_one != approx(1.0):
            raise ValueError(f"Proportions do not sum to 1, got {sum_to_one}")

    def __str__(self):
        return f"Chord Progression:\n{self.reference}"


# progression = pd.DataFrame(
#     {
#         "chords": [
#             "Cmaj Gmaj Am",
#             "Fmaj Cmaj Fmaj Cmaj",
#             "Fmaj Cmaj Gmaj Am Fmaj",
#         ]
#     }
# )
# kp2 = KeyPredictor()
# print(progression["chords"].apply(kp2.predict_key))
