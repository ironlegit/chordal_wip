import re
import pandas as pd


class ChordCanonizer:
    """
    ChordCanonizer for strict chord vocabulary (semantic validation):
    Decomposition of chords into properties, normalization and reconstruction

    Args:
        debugging (bool): Discarded remainder in parenthesis is added to the unclear property of the chord
    """

    # Pattern recognition ----
    ROOT_REGEX = re.compile(r"[A-G](?:#|b)?")

    # FIXME: Is there a good solution to this?
    # Justification for order of accidentals:
    # Leading "b" or "#" are much more frequent than "+" or "-"!
    # Trailing "+" or "-" are much more frequent than "b" or "#"!
    # Caveat: Some flat or sharp extensions are dropped or mixed up by this rule!
    EXTENSIONS_REGEX = re.compile(r"[#b]?(?:2|4|5|6|7|9|11|13){1}[+-]?")

    # Cave: Expression is greedy from left (up) to right (down)
    SPLIT_REGEX = re.compile(
        r"""
        \([^)]*\)
        |sus(?:2|4)?
        |add[#b]?(?:2|4|5|6|7|9|11|13){1}[+-]?
        |no[3|5|7](?:rd|th)?
        |mmaj
        |Maj
        |maj|M
        |min|m|-
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

    def __init__(self, debugging: bool = False):
        self._cached_chords = {}
        self.debugging = debugging

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

            # Handle rejections here
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
            "no": None,
            "slash": None,
            "unclear": [],
        }

        # Handle parenthesis content
        remainder = None
        if "(" in chord:
            chord, remainder = self._strip_parent_annotations(chord)

        if remainder and self.debugging:
            decomp_chord["unclear"].append(remainder)

        chord = chord.replace("(", "").replace(")", "")

        # Slash handling
        slash_tokens = None
        if "/" in chord:
            parts = chord.split("/")

            # Allows multiple slashes for later tokenization
            chord = "".join(parts[0:-1])

            # Only last slash is considered as real slash bass
            slash_bass_candidate = parts[-1]

            if self.ROOT_REGEX.match(slash_bass_candidate):
                decomp_chord["slash"] = slash_bass_candidate
            else:
                slash_tokens = slash_bass_candidate

        # Root handling
        root_capture = self.ROOT_REGEX.match(chord)

        if not root_capture:
            return decomp_chord

        root = root_capture.group(0)
        decomp_chord["root"] = root

        # Modifier handling
        remainder = chord[len(root) :]

        if slash_tokens:
            remainder += slash_tokens
        tokens = self.SPLIT_REGEX.findall(remainder)

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

            elif token.startswith("no"):
                decomp_chord["no"] = token.replace("rd", "").replace("th", "")

            else:
                decomp_chord["unclear"].append(token)

        return decomp_chord

    def _eval_parent_content(self, p_content: str) -> str:
        """
        Check whether a parenthesis content string is fully composed of valid chord tokens.

        Attempts to consume the entire string by repeatedly matching against SPLIT_REGEX
        from left to right. Returns True only if the string is fully consumed with no
        remainder, meaning every part of it is a recognised chord modifier.

        Examples:
            "min"   → True   (fully consumed in one match)
            "add9"  → True   (fully consumed in one match)
            "muted" → False  (remainder "uted" after matching "m")
            "strum" → False  (no match at all)
            "4x"    → False  (remainder "x" after matching "4")
        """
        # Iterate through the chord string consuming 1 token at the time from left to right.
        # Example: "maj7" → match "maj", remainder "7" → match "7", no remainder → exit
        p_content = p_content.replace("/", "")
        while p_content:
            match = self.SPLIT_REGEX.match(p_content)
            if not match:
                return False
            p_content = p_content[match.end() :]
        return True

    def _strip_parent_annotations(self, chord: str) -> str:
        """
        Remove parenthetical annotations that do not contain valid chord content.

        Iterates over all parenthetical groups in the chord string and removes those
        whose content is not recognised by _is_valid_paren_content. Parentheticals
        with valid chord content, such as (min) or (add9), are preserved.

        Examples:
            "A(strum)"  → "A"
            "A(muted)"  → "A"
            "A(4x)"     → "A"
            "A(min)"    → "A(min)"
            "Cmaj(add9" → "Cmaj(add9)"  (no change, not a closed parenthetical)
        """
        for match in re.finditer(r"\(([^)]*)\)", chord):
            p_content = match.group(1)
            remainder = None
            if not self._eval_parent_content(p_content):
                chord = chord.replace(match.group(0), "")
                remainder = match.group(0).replace("(", "").replace(")", "")
        return chord, remainder

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
            # not shorthand quality.
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
            and not decomp_chord["no"]  # TODO: Safe?
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

        # Handle extension removal logic
        no = decomp_chord["no"]
        if no:
            if no.endswith("3"):
                decomp_chord["quality"] = None
            elif no.endswith("5"):
                decomp_chord["quality_5th"] = None
            elif no.endswith("7"):
                decomp_chord["quality_7th"] = None
            else:
                decomp_chord["unclear"] = decomp_chord["no"]
                decomp_chord["no"] = None

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

        if decomp_chord["no"]:
            chord += "(n:" + decomp_chord["no"] + ")"

        if decomp_chord["slash"]:
            chord += "/" + decomp_chord["slash"]

        if decomp_chord["unclear"]:
            chord += "(u:" + ",".join(decomp_chord["unclear"]) + ")"

        return chord

    def _num_sort(self, txt: str):
        """
        Sort modifiers lists like `["add9", "add2", "add13"]` or alterations `[b9, #11]`
        Use this to generate index of dict.
        """
        numb = re.search(r"\d+", txt)

        if numb:
            return int(numb.group())

        return 999


test = "Cdim7M"
cc = ChordCanonizer()
print(cc.canonize(test))
