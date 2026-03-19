import re
from typing import Optional
import pandas as pd


class ChordCanonizer:
    """
    Aggressive standardization and selection
    """

    # Pattern recognition ----
    ROOT_REGEX = re.compile(r"[A-G](?:#|b)?")

    MAJOR_TRIAD_REGEX = re.compile(r"(M|Maj|maj)$")

    EXTENSIONS_REGEX = re.compile(r"[#b]?(?:2|4|5|6|7|9|11|13){1}[+-]?")

    SPLIT_REGEX = re.compile(
        r"""
        \([^)]*\)
        |sus(?:2|4)?
        |add(?:2|4|5|6|7|9|11|13){1}[#b+-]?
        |maj|M
        |dim
        |aug|\+
        |m|min|-
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
        "+": "aug",  # #TODO: This is by-passed!
    }

    # TODO: This should be generalized to e.g. <ROOT>13-
    EDGE_CASES = {"E13-": "Em13"}

    def __init__(self):
        self._cached_chords = {}

    # Public Method ----
    def canonicalize(self, txt: str):
        chords = txt.split(" ")
        chords_cleaned = []

        for chord in chords:
            if chord in self._cached_chords:
                if self._cached_chords[chord]:
                    chords_cleaned.append(chord)
                    continue

            # TODO: Dont like this part...
            if chord in self.EDGE_CASES:
                print(f"chord {chord} is an edge case!")
                chord_cleaned = self.EDGE_CASES[chord]
            else:
                # Canonization
                raw_decomposed_chord = self._decompose(chord)
                print(f"raw_decomposed_chord : {raw_decomposed_chord}")
                norm_decomposed_chord = self._normalize(raw_decomposed_chord)
                chord_cleaned = self._reconstruct(norm_decomposed_chord)
                print(f"chord_cleaned : {chord_cleaned}")

            if not chord_cleaned:
                self._cached_chords[chord] = False
                chords_cleaned.append("X")
                continue
            else:
                self._cached_chords[chord_cleaned] = True
            chords_cleaned.append(chord_cleaned)

        print(self._cached_chords)
        return " ".join(chords_cleaned)

    def save_cache(self):
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
            # "sus": None,
            "dominant": None,
            "adds": [],
            "extensions": [],
            # "alterations": [],
            "slash": None,
            "unclear": [],
        }

        chord = chord.replace("(", "").replace(")", "")

        tokens = []

        # Slash handling
        if "/" in chord:
            parts = chord.split("/")

            chord = "".join(parts[0:-1])  # Allows multiple slashes

            slash_bass_candidate = parts[-1]
            print(f"slash_bass_candidate : {slash_bass_candidate}")

            if self.ROOT_REGEX.match(slash_bass_candidate):
                decomp_chord["slash"] = slash_bass_candidate
            else:
                tokens.append(slash_bass_candidate)

        # Root handling
        root_capture = self.ROOT_REGEX.match(chord)

        if not root_capture:
            return decomp_chord

        root = root_capture.group(0)
        decomp_chord["root"] = root

        # Modifier handling
        remainder = chord[len(root) :]

        tokens = tokens + self.SPLIT_REGEX.findall(remainder)
        print(f"tokens : {tokens}")

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
        alterations = []
        for ext in decomp_chord["extensions"]:
            if ext == "2" or ext == "4":
                new_adds.append(f"add{ext}")
                continue

            if ext == "5+" or ext == "#5":
                # alterations.append("#5")
                decomp_chord["quality_5th"] = "aug"
                continue

            if ext == "7+":
                new_extensions.append("7")
                # alterations.append("#5")
                decomp_chord["quality_5th"] = "aug"
                continue

            ext = ext.replace("-", "b").replace("+", "#")

            if "#" in ext or "b" in ext:
                if ext[-1] in "#b":
                    ext = ext[-1] + ext[:-1]

            new_extensions.append(ext)

        # normalize adds and dedup add / extension overlap
        for add in decomp_chord["adds"]:
            add_extension_overlap = add.replace("add", "")
            if add_extension_overlap not in new_extensions:
                new_adds.append(add)
        decomp_chord["adds"] = sorted(set(new_adds), key=self._num_sort)

        major_triad = self._check_empty_dict_keys(
            decomp_chord, ["root", "adds", "slash"]
        )
        if major_triad:
            decomp_chord["quality"] = "maj"
            return decomp_chord

        # Define 7th
        has_seventh = any(
            ext in ["7", "9", "11", "13"] for ext in new_extensions
        )
        print(f"has_seventh : {has_seventh}")

        if has_seventh:
            new_extensions = [ext for ext in new_extensions if ext != "7"]
            if (
                decomp_chord["quality"] == "maj"
                and not decomp_chord["quality_5th"]
            ):
                print("1")
                decomp_chord["quality_7th"] = "maj"

            elif decomp_chord["quality"] == "m":
                print("2")
                decomp_chord["quality_7th"] = "m"

            elif decomp_chord["quality"] in ["sus2", "sus4"]:
                print("2.5")
                decomp_chord["quality_7th"] = "m"

            elif decomp_chord["quality"] == "mmaj":
                print("3")
                decomp_chord["quality_7th"] = "m"

            elif (
                decomp_chord["quality_5th"] == "aug"
                and not decomp_chord["quality"]
            ):
                print("4")
                decomp_chord["quality_7th"] = "m"

            # FIXME: Currently fixes edge case chords like "Cmaj7/#5"
            elif (
                decomp_chord["quality_5th"] == "aug"
                and decomp_chord["quality"] == "maj"
            ):
                print("5")
                decomp_chord["quality_7th"] = "maj"

            elif decomp_chord["quality_5th"] == "dim":
                print("6")
                decomp_chord["quality_7th"] = "dim"

            # FIXME: some candidates are prematurley excluded due to statement struct
            elif self._is_dominant(decomp_chord):
                # decomp_chord["dominant"] = True
                decomp_chord["quality"] = "maj"
                decomp_chord["quality_7th"] = "m"

        if decomp_chord["quality_5th"] == "aug" and not decomp_chord["quality"]:
            decomp_chord["quality"] = "maj"
            # TODO: remove explicit 5 if the chord is aug, example C+5.
            new_extensions = [ext for ext in new_extensions if ext != "5"]

        decomp_chord["extensions"] = sorted(
            set(new_extensions), key=self._num_sort
        )
        return decomp_chord

    # TODO: Should this be a formatter?
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

        if decomp_chord["dominant"]:
            chord += "(d:" + "True" + ")"

        if decomp_chord["adds"]:
            chord += "(m:" + ",".join(decomp_chord["adds"]) + ")"

        if decomp_chord["extensions"]:
            chord += "(e:" + ",".join(decomp_chord["extensions"]) + ")"

        if decomp_chord["slash"]:
            chord += "/" + decomp_chord["slash"]

        unclear = decomp_chord["unclear"]
        if unclear:
            chord += "(u:" + ",".join(unclear) + ")"

        return chord

    def _num_sort(self, txt: str):
        """
        Sort modifiers lists like `["add9", "add2", "add13"]` or alterations `[b9, #11]`
        """
        numb = re.search(r"\d+", txt)

        if numb:
            return int(numb.group())

        return 999

    def _check_empty_dict_keys(self, d: dict, ignore_keys: list):
        all_keys_empty = all(
            [
                val is None or val == []
                for key, val in d.items()
                if key not in ignore_keys
            ]
        )
        return all_keys_empty

    def _is_dominant(self, d: dict):
        """
        Check if a (decomposed) chord qualifies as a dominant chord.
            - Trigger function if any of 7, 9, 11, or 13 are in extensions
            - Major chords do not qualify as dominant, because the 7th is not minor.
            - Minor chords do not qualify as dominant, because the 3rd is not major.
            - Diminished chord do not qualify as dominant, because the 5th is diminished.
            - Suspended chord do not qualify as dominant, because they are lacking a 3rd.
        """
        if d["quality"] in ["maj", "m", "sus2", "sus4"]:
            return False

        if d["quality"] in ["dim"]:
            return False

        return True


cc = ChordCanonizer()

# TODO: aug mapping is by-passed, its not wrong but misleading!
test = "C+ Cm5+ F#7(5+) F#m(4)"
test = "C+ Caug Caug7 C7+"
test = "F#maj7(9,13)add6/E"


test = "C5+ C+5 C7+ Caug C+"

test = "Ebsus4(7)/C#"
# TODO: Handle qualities as list or two qualities?
# TODO: Define #5 as alteration or aug quality?
# test = "A4 A(4) Aadd4 Asus4"
o = cc.canonicalize(test)
print(f"t: {test}")
print(f"o : {o}")
