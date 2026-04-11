import re
from functools import lru_cache


class ChordFormatter:
    ROOT_REGEX = re.compile(r"^[A-G](?:#|b)?")
    TRIAD_MAP = {
        "q5:dim": "dim",
        "q3:maj": "maj",
        "q3:m": "m",
        "q3:sus": "maj",
    }

    def __init__(self, type="simple"):
        self.type = type
        self._cached_chords = {}

    def format(self, chords: str) -> str:
        # Converts
        chords_out = []

        for chord in chords.split():
            if chord in self._cached_chords:
                chords_out.append(self._cached_chords[chord])
                continue

            if chord == "X":
                chords_out.append(chord)
                continue

            root = self.ROOT_REGEX.match(chord)

            for pattern, quality in self.TRIAD_MAP.items():
                if pattern in chord:
                    chord_out = root.group() + quality
                    chords_out.append(chord_out)
                    self._cached_chords[chord] = chord_out
                    break

        return " ".join(chords_out)

    def _use_unicode_flat(self):
        """Convert b and dim to ♭ and °"""
        pass


import pandas as pd

# TODO: What about augmented?
cf = ChordFormatter()
chords = pd.DataFrame(
    {
        "chords": [
            "C#(q3:m)/A F#(q3:maj)/F G#(q3:m) C#(q3:m)",
            "F#(q3:maj) G#(q3:m) C#(q3:m) F#(q3:maj) G#(q3:m)",
            "C#(q3:m) F#(q3:maj) G#(q3:m) C#(q3:m) F#(q3:maj)",
            "G#(q3:sus2) C#(q3:m) F#(q3:maj) G#(q3:m) C#(q3:m)",
        ]
    }
)
print(chords["chords"].apply(cf.format))
