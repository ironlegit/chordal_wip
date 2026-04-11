import time
import pandas as pd
from chordal_wip.chordisolator import ChordIsolator
from chordal_wip.chordcanonizer import ChordCanonizer
from chordal_wip.chordformatter import ChordFormatter
from chordal_wip.key import KeyPredictor


class ChordProcessingPipeline:
    def __init__(self):
        self.isolator = ChordIsolator()
        self.canonizer = ChordCanonizer()
        self.formatter = ChordFormatter()
        self.keypredictor = KeyPredictor()

    def _print_header(self, stage, message):
        """Print a formatted box with the given stage and message."""
        # Content width
        box_inner = 48

        # Box
        title = stage.upper()
        print("╔" + "═" * box_inner + "╗")
        print("║" + title.center(box_inner) + "║")
        print("║" + message.center(box_inner) + "║")
        print("╚" + "═" * box_inner + "╝")

    def process(
        self, df: pd.DataFrame, input_column: str, write_cache: bool = False
    ) -> pd.DataFrame:
        # Isolation ----
        start_time = time.time()
        self._print_header("Chord Isolator", "CPP: Starting isolation...")

        df["chords_isolated"] = df[input_column].apply(self.isolator.isolate)
        duration = time.time() - start_time
        print(f"CPP: Isolation complete ({duration:.3f}s)")

        if write_cache:
            print("CPP: Writing isolated tokens cached_tokens.csv")
            self.isolator.write_cache()

        # Canonization ----
        self._print_header(
            "Chord Canonizer",
            "CPP: Starting canonization...",
        )
        start_time = time.time()
        df["chords_canonized"] = df["chords_isolated"].apply(
            self.canonizer.canonize
        )
        duration = time.time() - start_time
        print(f"CPP: Canonization complete ({duration:.3f}s)")

        if write_cache:
            print("CPP: Writing cached chords in cached_chords.csv")
            self.canonizer.write_cache()

        # Formatter ----
        self._print_header(
            "Chord Formatter",
            "CPP: Starting formatting...",
        )
        start_time = time.time()
        df["chords_simplified"] = df["chords_canonized"].apply(
            self.formatter.format
        )
        duration = time.time() - start_time
        print(f"CPP: Formatting complete ({duration:.3f}s)")

        # KeyPrediction ----
        self._print_header(
            "Key Prediction",
            "CPP: Predicting keys...",
        )
        start_time = time.time()
        df["key"] = df["chords_simplified"].apply(self.keypredictor.predict_key)
        duration = time.time() - start_time
        print(f"CPP: Key prediction complete ({duration:.3f}s)")

        print(f"CPP: Processed {len(df)} rows")

        return df
