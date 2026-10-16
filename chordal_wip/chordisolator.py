import re
from typing import Optional
import pandas as pd


class ChordIsolator:
    """
    ChordIsolator for lenient chord detection (structural validation):
    Tokenization, minimal normalization and rough selection of tokens based on chord structure.
    """

    def __init__(
        self,
        special_token_separator=r"(?<=\S)[,^%]{1}(?=\S)",
        char_threshold=20,
    ):
        self.char_threshold = char_threshold
        self.special_token_separator = special_token_separator
        self._root_regex = self._init_root_regex()
        self._chord_regex = self._init_chord_regex()
        self._cached_tokens = {}

    ROOT_NOTE_PATTERN = r"[A-G][#b]?"

    # Internal instance ----
    def _init_root_regex(self):
        return re.compile(self.ROOT_NOTE_PATTERN, re.VERBOSE)

    def _init_chord_regex(self):
        # Chord root
        root_note = self.ROOT_NOTE_PATTERN

        # Chord modifiers
        brackets = r"(?:\([^\)]*\))"  # match brackets with anything in it
        qualities = r"(?:maj|min|hdim|dim|aug|sus|add|m|M|no)"
        extensions = r"(?:2|4|5|6|7|9|10|11|13)"
        alterations = r"(?:[+#b-])"
        # Harte bass degrees: inversions are written as an interval, with the
        # modifier before the number, e.g. 'A:maj/3', 'C:min/b3'
        degrees = r"(?:[#b]*(?:1|2|3|4|5|6|7|8|9|10|11|12|13))"

        # Slash Logic
        # Option 1: root (Cm7/G)
        # Option 2: extension with leading or trailing accidental
        # Option 3: a quality OR some random chord modifier (Cm7/b5)
        # Option 4: Some single alterations
        # Option 5: a Harte bass degree (A:maj/3)   <- added to slash comments
        slash_content = rf"/(?:{root_note}|{alterations}?{extensions}{alterations}?|{qualities}|{alterations}|{degrees})+"

        # One modifier unit; a cluster is any run of these
        cluster_element = (
            rf"(?:{qualities}|{extensions}|{alterations}|{brackets}|{slash_content})"
        )
        cluster = rf"{cluster_element}*"

        # Harte qualifier: ':' directly after the root, e.g. 'G:7', 'A:min'.
        # At least one modifier must follow the colon, so bare tab-listing
        # fragments like 'G:' or 'Am7:' fail validation here as well.
        harte_qualifier = rf"(?::{cluster_element}{cluster})"

        # Full chord pattern
        chord_anatomy = rf"^{root_note}{harte_qualifier}?{cluster}$"

        return re.compile(chord_anatomy, re.VERBOSE)

    # Public Method ----
    def isolate(self, txt: str) -> str:
        tokens = self._tokenize(txt)
        tokens_list = self._process_tokens(tokens)
        return " ".join(tokens_list)

    def write_cache(self):
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
        # By default: Match ",", "^" or "%" within strings, i.e. not surrounded by whitespace
        txt = re.sub(self.special_token_separator, " ", txt)
        txt = re.sub(r"\s+", " ", txt)
        txt = txt.strip()
        return txt.split(" ")

    # Process list of tokens ----

    def _process_tokens(self, tokens: str) -> list:
        chords = []

        for token in tokens:
            token = self._erode(token)

            if not token:
                continue

            token = self._homogenize(token)

            cached = self._cached_tokens.get(token)

            if cached is not None:
                if cached:
                    chords.append(token)
                    continue
                else:
                    # Since token is junk, skip validation!
                    continue

            if self._reject(token):
                continue

            if self._validate(token):
                self._cached_tokens[token] = True
                chords.append(token)
            else:
                self._cached_tokens[token] = False

        return chords

    # Cleaning functions ----
    def _erode(self, token: str) -> str:
        """
        Strips leading non-note characters from a token.
        Returns the substring starting with the first valid note (A-G) or an empty string if none is found.
        """
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
        """Predicate that rejects tokens that are too long, resemble tabs or are unsplittable chord clusters"""

        # Rm long strings
        if len(token) >= self.char_threshold:
            return True

        # Rm tabs: root + dash/pipe, e.g. 'A|' ('G:' handled by the next rule)
        if re.match(r"^[A-G]{1}[#b]?[-|\s]{1,2}", token):
            return True

        # Rm colon junk: guitar tab listings like 'G:', 'Am7:', 'D/F#:'
        # Harte-qualified chords survive: the colon must be followed by a
        # Harte shorthand ('maj', 'min', 'hdim7', 'sus4', '7', ...), a digit
        # shorthand or a degree list '(' -- see Table 1 in Harte et al. 2005
        if re.match(r"^[A-G]{1}[#b]?:", token) and not re.match(
            r"^[A-G]{1}[#b]?:(?:maj|min|hdim|minmaj|dim|aug|sus|\d|\()", token
        ):
            return True

        # Rm coagulated strings, e.g. G7/E7/B7/E7 or G7-E7-B7-E7
        if len(re.findall(self._root_regex, token)) > 2:
            return True

        # Rm long numbers like strum notation 022100
        # TODO: Should this be a clean rather than a rejection?
        if re.search(r"[0-9]{3,}", token):
            return True

        return False

    def _validate(self, token: str) -> Optional[re.Match[str]]:
        """
        Validate whether the tokens follow an approximate chord structure
        """
        return self._chord_regex.match(token)
