import time
from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd

from chordal_wip.chordcanonizer import ChordCanonizer
from chordal_wip.chordformatter import ChordFormatter
from chordal_wip.chordisolator import ChordIsolator


@dataclass
class PipelineStep:
    """One column-to-column transform in the pipeline.

    The function is a BOUND METHOD (e.g. self.isolator.isolate): a value
    that remembers its instance - so 'transform' behaves like one of your
    purrr function lists, applied stage by stage.
    """

    name: str  # for logging: "Chord Isolator"
    transform: Callable[[str], str]  # stage function
    output_column: str  # result column name
    write_cache: Callable[[], None] | None = None  # cache dump (optional)


class ChordProcessingPipeline:
    """
    Transforms raw chord text to standardized chord notation
    """

    def __init__(self):
        self.isolator = ChordIsolator()
        self.canonizer = ChordCanonizer()
        self.formatter = ChordFormatter()

        self._steps = [
            PipelineStep(
                "Chord Isolator",
                self.isolator.isolate,
                "chords_isolated",
                self.isolator.write_cache,
            ),
            PipelineStep(
                "Chord Canonizer",
                self.canonizer.canonize,
                "chords_canonized",
                self.canonizer.write_cache,
            ),
            PipelineStep("Chord Formatter", self.formatter.format, "chords_simplified"),
        ]

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
        df = df.copy()
        current = input_column

        for step in self._steps:
            start = time.time()
            self._print_header(step.name, "CPP: starting...")
            df[step.output_column] = df[current].apply(step.transform)
            print(f"CPP: {step.name} complete ({time.time() - start:.3f}s)")

            if write_cache and step.write_cache:
                step.write_cache()

            current = step.output_column

        return df
