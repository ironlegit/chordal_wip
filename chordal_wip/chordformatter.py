class ChordFormatter:
    def __init__(self, verbose_chord):
        self.tidy_chord = self.tidy_up(verbose_chord)

    def tidy_up(self):
        pass

    def _format_extensions(self, extensions):
        extensions_formatted = ""
        if extensions:
            extensions_formatted += extensions[0]
            if len(extensions) > 1:
                extensions_formatted += "(e:" + ",".join(extensions[1:]) + ")"
