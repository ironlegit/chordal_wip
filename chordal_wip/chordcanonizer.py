import re
import pandas as pd


class ChordCanonizer:
    """
    Decomposition of chords into properties, normalization and reconstruction
    """

    # Pattern recognition ----
    ROOT_REGEX = re.compile(r"[A-G](?:#|b)?")

    EXTENSIONS_REGEX = re.compile(r"[#b]?(?:2|4|5|6|7|9|11|13){1}[+-]?")

    SPLIT_REGEX = re.compile(
        r"""
        \([^)]*\)
        |sus(?:2|4)?
        |add[#b]?(?:2|4|5|6|7|9|11|13){1}[+-]?
        |mmaj
        |Maj
        |maj|M
        |m|min|-
        |dim
        |aug|\+
        |[#b]?(?:2|4|5|6|7|9|11|13){1}[+-]?
        """,
        re.VERBOSE,
    )

    ALLOWED_QUALITIES = {
        "min": "m",
        "m": "m",
        "-": "m",
        "maj": "maj",
        "Maj": "maj",
        "M": "maj",
        "mmaj": "mmaj",
        "sus": "sus4",
        "sus4": "sus4",
        "sus2": "sus2",
    }

    ALLOWED_QUALITIES_5TH = {
        "dim": "dim",
        "aug": "aug",
        "+": "aug",
    }

    def __init__(self):
        self._cached_chords = {}

    # Public Method ----
    def canonize(self, txt: str):
        chords = txt.split(" ")
        chords_cleaned = []

        for chord in chords:
            if chord in self._cached_chords:
                chords_cleaned.append(self._cached_chords[chord])
                continue

            # Canonization
            raw_decomposed_chord = self._decompose(chord)
            norm_decomposed_chord = self._normalize(raw_decomposed_chord)
            chord_cleaned = self._reconstruct(norm_decomposed_chord)

            result = chord_cleaned if chord_cleaned else "X"
            self._cached_chords[chord] = result
            chords_cleaned.append(result)

        return " ".join(chords_cleaned)

    def write_cache(self):
        df = pd.DataFrame.from_dict(
            self._cached_chords, orient="index", columns=["value"]
        )
        df.index.name = "chord"
        df.reset_index(inplace=True)
        df.to_csv("cached_chords.csv")

    # Private Methods ----
    def _decompose(self, chord: str) -> dict:
        decomp_chord = {
            "root": None,
            "quality": None,
            "quality_5th": None,
            "quality_7th": None,
            "adds": [],
            "extensions": [],
            "slash": None,
            "unclear": [],
        }

        chord = chord.replace("(", "").replace(")", "")

        slash_tokens = []

        # Slash handling
        if "/" in chord:
            parts = chord.split("/")

            chord = "".join(parts[0:-1])  # Allows multiple slashes

            slash_bass_candidate = parts[-1]

            if self.ROOT_REGEX.match(slash_bass_candidate):
                decomp_chord["slash"] = slash_bass_candidate
            else:
                slash_tokens.append(slash_bass_candidate)

        # Root handling
        root_capture = self.ROOT_REGEX.match(chord)

        if not root_capture:
            return decomp_chord

        root = root_capture.group(0)
        decomp_chord["root"] = root

        # Modifier handling
        remainder = chord[len(root) :]

        tokens = slash_tokens + self.SPLIT_REGEX.findall(remainder)

        for token in tokens:
            token = token.strip()

            if token.startswith("add"):
                decomp_chord["adds"].append(token)

            elif token in self.ALLOWED_QUALITIES_5TH:
                decomp_chord["quality_5th"] = self.ALLOWED_QUALITIES_5TH[token]

            elif token in self.ALLOWED_QUALITIES:
                decomp_chord["quality"] = self.ALLOWED_QUALITIES[token]

            elif self.EXTENSIONS_REGEX.match(token):
                decomp_chord["extensions"].append(token)

            else:
                decomp_chord["unclear"].append(token)

        return decomp_chord

    def _normalize(self, decomp_chord: dict) -> dict:
        # normalize extensions
        new_extensions = []
        new_adds = []
        for ext in decomp_chord["extensions"]:
            if ext == "2" or ext == "4":
                new_adds.append(f"add{ext}")
                continue

            # Augmented 5th shorthands — conventional and unambiguous, always a quality
            # signal regardless of how many extensions are present. 7+ is included here
            # because it is a well-established jazz shorthand for dom7#5, not a sharp 7.
            if ext in ("5+", "#5", "7+"):
                decomp_chord["quality_5th"] = "aug"
                # keep 7 for the has_seventh check later
                if ext == "7+":
                    new_extensions.append("7")
                continue

            # Trailing - / + are ambiguous: quality signal (E13- = Em13) or pitch
            # alteration (Gmaj7/9- = Gmaj7b9). These symbols are treated as quality
            # signal only when they are the sole extension AND no explicit quality
            # has been parsed.
            # Multiple extensions imply the writer was specifying intervals precisely,
            # not shorthand quality. Note: 7+ is now handled here, removing the need
            # for the old special case.
            if ext.endswith("-") and ext[0] not in ("#", "b"):
                if (
                    len(decomp_chord["extensions"]) == 1
                    and decomp_chord["quality"] is None
                ):
                    decomp_chord["quality"] = "m"
                    ext = ext[:-1]

                # trailing - becomes flat prefix after reorder below
                else:
                    ext = ext[:-1] + "b"

            elif ext.endswith("+") and ext[0] not in ("#", "b"):
                if (
                    len(decomp_chord["extensions"]) == 1
                    and decomp_chord["quality"] is None
                ):
                    decomp_chord["quality_5th"] = "aug"
                    ext = ext[:-1]

                # trailing + becomes sharp prefix after reorder below
                else:
                    ext = ext[:-1] + "#"

            if "#" in ext or "b" in ext:
                # Normalise suffix-style accidentals: "9b" → "b9"
                if ext[-1] in "#b":
                    ext = ext[-1] + ext[:-1]

            new_extensions.append(ext)

        # Handle alternative dim or half-dim notation
        if "b5" in new_extensions:
            decomp_chord["quality_5th"] = "dim"
            new_extensions = [ext for ext in new_extensions if ext != "b5"]

        # normalize adds and dedup add / extension overlap
        for add in decomp_chord["adds"]:
            add_extension_overlap = add.replace("add", "")
            if add_extension_overlap not in new_extensions:
                new_adds.append(add)
        decomp_chord["adds"] = sorted(set(new_adds), key=self._num_sort)

        major_triad = (
            not new_extensions
            and not decomp_chord["quality"]
            and not decomp_chord["quality_5th"]
            and not decomp_chord["quality_7th"]
        )

        if major_triad:
            decomp_chord["quality"] = "maj"
            decomp_chord["extensions"] = new_extensions
            return decomp_chord

        # 6th chords have no implied 7th — 6 replaces the 7th in these voicings
        has_sixth = any(self._num_sort(ext) == 6 for ext in new_extensions)
        has_seventh = not has_sixth and any(
            self._num_sort(ext) in {7, 9, 11, 13} for ext in new_extensions
        )

        if has_seventh:
            new_extensions = [
                ext for ext in new_extensions if self._num_sort(ext) != 7
            ]

            q, q5 = decomp_chord["quality"], decomp_chord["quality_5th"]

            if q == "mmaj":
                decomp_chord["quality"] = "m"
                decomp_chord["quality_7th"] = "maj"
            elif q == "maj":
                decomp_chord["quality_7th"] = "maj"
            # Handle half-dim (b5) and full-dim (b5, b7)
            elif q5 == "dim":
                decomp_chord["quality_7th"] = "dim" if q is None else "m"
            else:
                decomp_chord["quality_7th"] = "m"
                if q is None:
                    decomp_chord["quality"] = "maj"  # dominant

        # Edge cases
        if decomp_chord["quality_5th"] == "aug" and not decomp_chord["quality"]:
            decomp_chord["quality"] = "maj"
            # TODO: remove explicit 5 if the chord is aug, example C+5.
            new_extensions = [
                ext for ext in new_extensions if self._num_sort(ext) != 5
            ]

        # Fallback: any remaining chord without an explicit quality defaults to major
        # Excludes dim (quality_5th set) and sus/aug (quality already set above)
        if not decomp_chord["quality"] and not decomp_chord["quality_5th"]:
            decomp_chord["quality"] = "maj"

        decomp_chord["extensions"] = sorted(
            set(new_extensions), key=self._num_sort
        )
        return decomp_chord

    # What is the benefit from decomposing > string > reformatting?
    # Wouldnt be decomposing > formatting make more sense?
    # Reconstruct could use a formatter class that has different options.
    # This version could be a raw format?
    def _reconstruct(self, decomp_chord: dict) -> str:
        if not decomp_chord["root"]:
            return None

        chord = decomp_chord["root"]

        if decomp_chord["quality"]:
            chord += "(q3:" + decomp_chord["quality"] + ")"

        if decomp_chord["quality_5th"]:
            chord += "(q5:" + decomp_chord["quality_5th"] + ")"

        if decomp_chord["quality_7th"]:
            chord += "(q7:" + decomp_chord["quality_7th"] + ")"

        if decomp_chord["adds"]:
            chord += "(m:" + ",".join(decomp_chord["adds"]) + ")"

        if decomp_chord["extensions"]:
            chord += "(e:" + ",".join(decomp_chord["extensions"]) + ")"

        if decomp_chord["slash"]:
            chord += "/" + decomp_chord["slash"]

        if decomp_chord["unclear"]:
            chord += "(u:" + ",".join(decomp_chord["unclear"]) + ")"

        return chord

    def _num_sort(self, txt: str):
        """
        Sort modifiers lists like `["add9", "add2", "add13"]` or alterations `[b9, #11]`
        """
        numb = re.search(r"\d+", txt)

        if numb:
            return int(numb.group())

        return 999
