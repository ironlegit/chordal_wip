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
