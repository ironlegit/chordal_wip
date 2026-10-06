import chordal_wip.scales as scales
import pandas as pd
from collections import Counter
from scipy.sparse import csr_matrix
import numpy as np
from dataclasses import dataclass


# Map note names to pitch classes (C=0, C#=1, ..., B=11).
# This is used to measure distance between keys and note names
NOTE_TO_PITCH_CLASS = {
    note: pc for pc, note in enumerate(scales.Scale.ALL_NOTES.tolist())
}


def _softmax(x: np.ndarray) -> np.ndarray:
    """
    Convert raw scores into probabilities that sum to 1.

    exp() spreads scores apart (a key that scores a bit higher becomes
    meaningfully more likely), then dividing by the total turns the
    result into a probability distribution.

    Why 'x - x.max()'? exp() overflows for large inputs. Subtracting the
    max first shrinks numerator and denominator by the same factor, so
    the result is unchanged - only the numbers stay small enough for
    float math. Standard numerical-stability trick.
    """
    e = np.exp(x - x.max())
    return e / e.sum()


def key_relation(tonic_a: str, mode_a: str, tonic_b: str, mode_b: str) -> str:
    """
    Classify how two keys are related.

    Returns 'exact', 'relative', 'parallel', 'fifth' or 'other'.

    Why this matters: predicting 'C ionian' for a song really in A
    aeolian (its relative pair) is a benign error, since both keys contain
    exactly the same chords. Confusing C ionian with F# aeolian is not.
    """
    if (tonic_a, mode_a) == (tonic_b, mode_b):
        return "exact"

    # Calculate distance around 12-semitone circle
    d = (NOTE_TO_PITCH_CLASS[tonic_a] - NOTE_TO_PITCH_CLASS[tonic_b]) % 12

    # Find shortest way around the circle
    distance = min(d, 12 - d)
    modes_differ = mode_a != mode_b

    # same tonic, different mode (C ionian vs C aeolian)
    if distance == 0 and modes_differ:
        return "parallel"

    # relative major/minor (C ionian vs A aeolian)
    if distance == 3 and modes_differ:
        return "relative"

    # dominant or subdominant (C ionian vs G or F ionian)
    if distance == 5:
        return "fifth"

    return "other"


@dataclass
class KeyPrediction:
    """Result of one key prediction.

    @dataclass auto-generates __init__, __repr__ and __eq__ from these
    typed fields - so printing a KeyPrediction (in tests, in the debugger)
    shows everything without writing any boilerplate.
    """

    tonic: str  # root key
    mode: str  # currently "ionian" or "aeolian"
    probs: np.ndarray  # probability per reference key; 24 values; sums to 1
    n_chords: int  # length of input chord progression
    oov_fraction: float  # fraction of tokens that are broken

    @property
    def label(self) -> str:
        """
        Human-readable key output, e.g. 'C ionian'.
        """
        return f"{self.tonic} {self.mode}"

    @property
    def confidence(self) -> float:
        """
        Probability of the winning key, between 0 and 1.
        """
        return float(self.probs.max())

    @property
    def margin(self) -> float:
        """
        Relative gap between the best and second-best key (0 to 1).

        Near 0 means the top two keys were almost equally likely, which
        in practice happens exactly for relative major/minor pairs.
        This is the number you will later filter on.
        """
        top2 = np.sort(self.probs)[::-1][:2]
        return float((top2[0] - top2[1]) / top2[0])


class KeyPredictor:
    """
    A class for predicting key from a chord progression.
    """

    def __init__(self):
        # Reference containing scale definition for all keys
        self.reference = scales.get_ref_scales()

        # Weight-matrix of all scales (rows) and all chords (cols) >> very sparse
        self.weights_df = pd.DataFrame.from_records(
            self.reference["chord_weights"]
        ).fillna(0)  # Convert NaN to 0 for weight mat mult

        # Init pre-allocated arrays for chord proportion computation
        self.chord_columns = self.weights_df.columns
        self.chord_to_idx = {chord: idx for idx, chord in enumerate(self.chord_columns)}
        self.len_prop_vector = len(self.chord_columns)

        # Sparse matrix only stores position of non-zero values
        self.weights_sparse = csr_matrix(self.weights_df.values)
        self.n_scales = len(self.reference)

    # Public methods
    def predict(self, chords: str) -> KeyPrediction | None:
        chord_list = chords.split()

        if not chord_list:
            return None

        n_chords = len(chord_list)
        counts = Counter(chord_list)

        # Build proportion vector
        prop_vector = np.zeros(self.len_prop_vector)
        n_known = 0

        for chord, count in counts.items():
            if chord in self.chord_to_idx:
                prop_vector[self.chord_to_idx[chord]] = count / n_chords
                n_known += count

        # Avoid returning first scale (i.e. C ionian) if all chords are broken
        if n_known == 0:
            return None

        # Compute scores
        scores = self.weights_sparse.dot(prop_vector)
        probs = _softmax(scores)

        max_score_idx = np.argmax(probs)

        ref_max = self.reference.iloc[max_score_idx]

        return KeyPrediction(
            tonic=ref_max["key"],
            mode=ref_max["mode"],
            probs=probs,
            n_chords=n_chords,
            oov_fraction=1 - n_known / n_chords,
        )

    def predict_key(self, chords: str) -> str | None:
        """
        Convenience wrapper: just the label. Existing call sites keep
        working unchanged - new code should prefer predict().
        """
        prediction = self.predict(chords)
        return prediction.label if prediction else None

    def __str__(self):
        return f"Chord Progression:\n{self.reference}"


kp = KeyPredictor()
clear = kp.predict("Cmaj Gmaj Am Fmaj Cmaj Fmaj Cmaj Gmaj Cmaj")
tie = kp.predict("Cmaj Am Fmaj Gmaj")
print(clear.label, round(clear.confidence, 3), round(clear.margin, 3))
print(tie.label, round(tie.confidence, 3), round(tie.margin, 3))

# kp = KeyPredictor()
# progression = "Dm Dm Amaj Gmaj Dm Dm Amaj Gmaj Bm Amaj Gmaj Amaj Dm Dm Amaj Gmaj Bm Amaj Gmaj Amaj Dm Dm Amaj Gmaj Bm Amaj Gmaj Amaj Dm"
# print(kp.predict_key(progression))
