import time
import pandas as pd
from chordal_wip.chordisolator import ChordIsolator
from chordal_wip.chordcanonizer import ChordCanonizer


class ChordProcessingPipeline:
    def __init__(self):
        self.isolator = ChordIsolator()
        self.canonizer = ChordCanonizer()

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
        duration_isolation = time.time() - start_time
        print(f"CPP: Isolation complete ({duration_isolation:.3f}s)")

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
        duration_canonization = time.time() - start_time
        print(f"CPP: Canonization complete ({duration_canonization:.3f}s)")

        print(f"CPP: Processed {len(df)} rows")

        if write_cache:
            print("CPP: Writing cached chords in cached_chords.csv")
            self.canonizer.write_cache()

        return df
