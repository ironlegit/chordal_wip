import re


class ChordFormatter:
    ROOT_REGEX = re.compile(r"^[A-G](?:#|b)?")
    TRIAD_MAP = {
        "(q5:dim)": "dim",
        "(q3:maj)": "maj",
        "(q3:m)": "m",
    }

    def __init__(self, type="simple"):
        self.type = type

    def format(self, chords: str) -> str:
        if self.type == "simple":
            chords_out = []

            for chord in chords.split():
                root = self.ROOT_REGEX.match(chord).group()
                for pattern, quality in self.TRIAD_MAP.items():
                    if pattern in chord:
                        chords_out.append(root + quality)

        return " ".join(chords_out)

    def _use_unicode_flat(self):
        """Convert b and dim to ♭ and °"""
        pass


cf = ChordFormatter()

chords = "C#(q3:m) F#(q3:maj) G#(q3:m) C#(q3:m) F#(q3:maj) G#(q3:m) C#(q3:m) F#(q3:maj) G#(q3:m) C#(q3:m) F#(q3:maj) G#(q3:m) C#(q3:m) F#(q3:maj) G#(q3:m) C#(q3:m) F#(q3:maj) G#(q3:m) C#(q3:m) F#(q3:maj) G#(q3:m) C#(q3:m) F#(q3:maj) G#(q3:m) C#(q3:m) F#(q3:maj) G#(q3:m) C#(q3:m) F#(q3:maj) G#(q3:m)"

print(cf.format(chords))
