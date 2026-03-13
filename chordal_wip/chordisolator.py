import re
from typing import Optional
import pandas as pd


class ChordIsolator:
    """
    Lenient chord detection:
    Tokenization, minimal normalization and rough selection of tokens based on chord structure.
    """

    def __init__(self, char_threshold=20):
        self.char_threshold = char_threshold
        self._chord_regex = self._init_chord_regex()
        self._cached_tokens = {}

    # Internal instance ----
    def _init_chord_regex(self):
        # Chord root
        root = "[A-G]{1}"
        accidental = "[#b]?"
        root_note = rf"{root}{accidental}"

        # Chord modifiers
        brackets = r"(?:\([^\)]*\))"  # match brackets with anything in it
        qualities = r"(?:maj|min|dim|aug|sus|add|m|M)"
        extensions = r"(?:2|4|5|6|7|9|10|11|13)"
        alterations = r"(?:[+#-])"

        # Slash Logic
        # Either root (Cm7/G) OR some random chord modifier (Cm7/b5)
        slash_content = rf"/(?:{root_note}|{accidental}?{extensions}|{qualities}|{alterations})+"

        # Cluster
        cluster = rf"(?:{qualities}|{extensions}|{alterations}|{brackets}|{slash_content})*"

        # Full chord pattern
        chord_anatomy = rf"^{root_note}{cluster}$"

        return re.compile(chord_anatomy, re.VERBOSE)

    # Public Method ----
    def raw_chord_isolation(self, txt: str) -> str:
        tokens = self._tokenize(txt)
        tokens_list = self._process_tokens(tokens)
        return " ".join(tokens_list)

    def save_cache(self):
        df = pd.DataFrame.from_dict(
            self._cached_tokens, orient="index", columns=["value"]
        )
        df.index.name = "chord"
        df.reset_index(inplace=True)
        df.to_csv("cached_tokens.csv")

    # Private Methods ----

    # Tokenize ----
    def _tokenize(self, txt: str) -> list:
        """Split by coma and rm leading, trailing, and excess whitespaces, i.e. n > 1"""
        split_symbol_pattern = r"(?<=\S)[,^%]{1}(?=\S)"
        txt = re.sub(split_symbol_pattern, " ", txt)
        txt = re.sub(r"\s+", " ", txt)
        txt = txt.strip()
        return txt.split(" ")

    # Process list of tokens ----

    def _process_tokens(self, tokens: str) -> list:
        chords = []

        for token in tokens:
            token = self._erode(token)

            if not token:
                # print("Empty token")
                continue

            token = self._homogenize(token)

            cached = self._cached_tokens.get(token)

            if cached is not None:
                # print(f"{token} already in cache!")
                if cached:
                    chords.append(token)
                    continue
                else:
                    # Since token is junk, skip validation!
                    continue

            if self._reject(token):
                # print(f"{token} rejected!")
                continue

            if self._validate(token):
                # print(f"{token} validated and cached!")
                self._cached_tokens[token] = True
                chords.append(token)
            else:
                # print(f"{token} added to cache as junk")
                self._cached_tokens[token] = False

        return chords

    # Cleaning functions ----
    def _erode(self, token: str) -> str:
        """
        Strips leading non-note characters from a token.
        Returns the substring starting with the first valid note (A-G) or an empty string if none is found.
        """
        # Or use regex? ^[^A-G]+

        for i, c in enumerate(token):
            if c in "ABCDEFG":
                return token[i:]
        return ""

    def _homogenize(self, token: str) -> str:
        """
        Convert Unicode music symbols to ASCII and remove superfluous symbols.
        """
        # Convert Unicode to ASCII
        token = token.replace("♭", "b")
        token = token.replace("♯", "#")
        token = token.replace("°", "dim")
        token = token.replace("–", "-")

        # Strip trailing symbol leftovers
        token = token.rstrip("*~,/")

        return token

    def _reject(self, token: str) -> bool:
        """Predicate that rejects tokens that are too long or resemble tabs"""
        if len(token) >= self.char_threshold:
            # print(f"{token} too long")
            return True

        if re.match(r"^[A-G]{1}[#b]?[-|:\s]{1,2}", token):
            # print(f"{token} is a tab!")
            return True

        return False

    def _validate(self, token: str) -> Optional[re.Match[str]]:
        """
        Validate whether the tokens follow an approximate chord structure
        """
        return self._chord_regex.match(token)


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
        |sus(?:2|4)
        |add(?:2|4|5|6|7|9|11|13){1}[#b+-]?
        |maj|M
        |dim
        |aug|\+
        |m|min
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
        "dim": "dim",  # TODO: Consider ° as full diminished?
        "aug": "aug",
        "+": "aug",
        "sus": "sus4",
        "sus4": "sus4",
        "sus2": "sus2",
    }

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
                norm_decomposed_chord = self._normalize(raw_decomposed_chord)
                chord_cleaned = self._reconstruct(norm_decomposed_chord)

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
        df.to_csv("cache.csv")

    # Private Methods ----
    def _decompose(self, chord: str) -> dict:
        decomp_chord = {
            "root": None,
            "quality": None,
            "adds": [],
            "sus": None,
            "dominant": None,
            "extensions": [],
            "alterations": [],
            "slash": None,
            "unclear": [],
        }

        chord = chord.replace("(", "").replace(")", "")

        tokens = []

        # Slash handling
        if "/" in chord:
            parts = chord.split("/")

            chord = parts[0]

            slash_bass_candidate = parts[-1]

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

        for token in tokens:
            token = token.strip()

            if token.startswith("add"):
                decomp_chord["adds"].append(token)

            elif token.startswith("sus"):
                decomp_chord["sus"] = self.ALLOWED_QUALITIES[token]

            elif token in self.ALLOWED_QUALITIES:
                decomp_chord["quality"] = self.ALLOWED_QUALITIES[token]

            elif self.EXTENSIONS_REGEX.match(token):
                decomp_chord["extensions"].append(token)

            else:
                decomp_chord["unclear"].append(token)

        return decomp_chord

    def _normalize(self, decomp_chord: dict) -> dict:
        if decomp_chord["quality"] == "aug":
            decomp_chord["quality"] = ""
            decomp_chord["alterations"].append("#5")

        # normalize adds and dedup add / extension overlap
        new_adds = []
        for add in decomp_chord["adds"]:
            add_extension_overlap = add.replace("add", "")
            if add_extension_overlap not in decomp_chord["extensions"]:
                new_adds.append(add)
        decomp_chord["adds"] = sorted(set(new_adds), key=self._num_sort)

        # normalize extensions
        new_extensions = []
        alterations = []
        for ext in decomp_chord["extensions"]:
            print(f"ext: {ext}")
            if ext == "5+":
                alterations.append("#5")
                continue

            if ext == "7+":
                new_extensions.append("7")
                alterations.append("#5")
                continue

            ext = ext.replace("-", "b").replace("+", "#")
            if "#" in ext or "b" in ext:
                if ext[-1] in "#b":
                    ext = ext[-1] + ext[:-1]

            new_extensions.append(ext)

        decomp_chord["extensions"] = sorted(
            set(new_extensions), key=self._num_sort
        )

        decomp_chord["alterations"] = sorted(
            set(alterations + decomp_chord["alterations"]), key=self._num_sort
        )
        # TESTING: Major triad check
        major_triad = self._check_empty_dict_keys(
            decomp_chord, ["root", "slash"]
        )
        if major_triad:
            decomp_chord["quality"] = "maj"

        # TESTING: Does it work consistently?
        if self._is_dominant(decomp_chord):
            decomp_chord["dominant"] = True

        return decomp_chord

    def _reconstruct(self, decomp_chord: dict) -> str:
        if not decomp_chord["root"]:
            return None

        chord = decomp_chord["root"]

        if decomp_chord["quality"]:
            chord += "(q:" + decomp_chord["quality"] + ")"

        if decomp_chord["adds"]:
            chord += "(m:" + ",".join(decomp_chord["adds"]) + ")"

        if decomp_chord["sus"]:
            chord += "(s:" + decomp_chord["sus"] + ")"

        if decomp_chord["dominant"]:
            chord += "(d:" + "True" + ")"

        if decomp_chord["extensions"]:
            chord += "(e:" + ",".join(decomp_chord["extensions"]) + ")"

        if decomp_chord["alterations"]:
            chord += "(a:" + ",".join(decomp_chord["alterations"]) + ")"

        if decomp_chord["slash"]:
            chord += "/" + decomp_chord["slash"]

        unclear = decomp_chord["unclear"]
        if unclear:
            chord += "(u:" + ",".join(unclear) + ")"

        return chord

    def _num_sort(self, txt: str):
        """
        Sort modifiers lists like `["add9", "add2", "add13"]`
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
        if d["quality"] in ["maj", "m"]:
            return False

        has_seventh = any(
            ext in ["7", "9", "11", "13"] for ext in d["extensions"]
        )

        return has_seventh


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


# TODO: Check if aug works fine now and add  tests for sus/aug/slashi/6 chords!!
# TODO: Dominance does not work!
#
# cc = ChordCanonizer()
#
# test = pd.Series(["Amin Bmin Cmin", "Amaj Bmaj Cmaj"])
#
# res = test.apply(cc.canonicalize)
#
# cc.save_cache()
# print(f"out : {res}")
