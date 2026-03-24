class ChordFormatter:
    def __init__(self, type="default"):
        self.type = type
        self.tidy_chord = self.tidy_up(self.type)

    def tidy_up(self, type: str) -> str:
        pass

    def _use_unicode_flat(self):
        """Convert b and dim to ♭ and °"""
        pass

    def _format_extensions(self, extensions):
        extensions_formatted = ""
        if extensions:
            extensions_formatted += extensions[0]
            if len(extensions) > 1:
                extensions_formatted += "(e:" + ",".join(extensions[1:]) + ")"


cf = ChordFormatter()
