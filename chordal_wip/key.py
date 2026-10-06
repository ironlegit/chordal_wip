import chordal_wip.scales as scales
import pandas as pd
from collections import Counter
from scipy.sparse import csr_matrix
import numpy as np
from dataclasses import dataclass


@dataclass
class KeyPrediction:
    """Result of one key prediction.

    @dataclass auto-generates __init__, __repr__ and __eq__ from these
    typed fields - so printing a KeyPrediction (in tests, in the debugger)
    shows everything without writing any boilerplate.
    """

    tonic: str  # root key
    mode: str  # currently "ionian" or "aeolian"
    scores: np.ndarray  # raw key prediction score per reference key
    n_chords: int  # length of input chord progression
    oov_fraction: float  # fraction of tokens that are broken

    @property
    def label(self) -> str:
        """
        Human-readable key output, e.g. 'C ionian'.
        """
        return f"{self.tonic} {self.mode}"


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
    def predict_key(self, chords: str) -> str | None:
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
        max_score_idx = np.argmax(scores)

        ref_max = self.reference.iloc[max_score_idx]
        return f"{ref_max['key']} {ref_max['mode']}"

    def __str__(self):
        return f"Chord Progression:\n{self.reference}"


# kp = KeyPredictor()
# progression = "Dm Dm Amaj Gmaj Dm Dm Amaj Gmaj Bm Amaj Gmaj Amaj Dm Dm Amaj Gmaj Bm Amaj Gmaj Amaj Dm Dm Amaj Gmaj Bm Amaj Gmaj Amaj Dm"
# print(kp.predict_key(progression))
