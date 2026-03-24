import time
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
        print("╔" + "═" * box_inner + "╗")
        title = stage.upper()
        print("║" + title.center(box_inner) + "║")
        print("║" + message.center(box_inner) + "║")
        print("╚" + "═" * box_inner + "╝")

    def process(self, df, input_column):
        # Isolation ----
        start_time = time.time()
        self._print_header("Chord Isolator", "CPP: Starting isolation...")

        df["chords_isolated"] = df[input_column].apply(self.isolator.isolate)
        duration_isolation = time.time() - start_time
        print(f"CPP: Isolation complete ({duration_isolation:.3f}s)")

        # Canonization ----
        self._print_header(
            "Chord Canonizer",
            "CPP: Starting canonization...",
        )
        start_time = time.time()
        df["chords_canonized"] = df["chords_isolated"].apply(
            self.canonizer.canonize
        )
        duration_canonization = (time.time() - start_time) * 1000
        print(f"CPP: Canonization complete ({duration_canonization:.3f}s)")

        print(f"CPP: Processed {len(df)} rows.")

        return df
