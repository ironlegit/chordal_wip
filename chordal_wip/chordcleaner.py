import re
from typing import Optional


class ChordCleaner:
    """
    A class for cleaning and standardizing chord notations in text data.
    """

    def __init__(self, freq_threshold=None, char_threshold=20):
        self.freq_threshold = freq_threshold
        self.char_threshold = char_threshold

    # Tokenize ----
    def _split_strings(self, txt):
        # Note: Do not include - since there are often tabs in the chord data
        split_comma_pattern = r"(?<=\S),(?=\S)"
        return re.sub(split_comma_pattern, " ", txt)

    # Clean up ----

    def _rm_long_words(self, txt):
        long_word_pattern = rf"\S{{{self.char_threshold},}}"
        return re.sub(long_word_pattern, "", txt)

    def _rm_tab_notation(self, txt):
        """Remove tablature notation from the text."""
        # This pattern looks for sequences with many dashes and numbers
        # tab_pattern = r"\b[A-G]#?b?\|{1,2}[-0-9hpsbrv?\/]+[\| ]+"
        tab_pattern = r"\b[A-G]#?b?\|{1,2}[-0-9hpsbrv?\/]+[\| ]+"
        return re.sub(tab_pattern, "", txt)

    def _rm_whitespace(self, txt):
        """Remove leading, trailing and excess whitespaces, i.e. n>1."""
        txt = re.sub(r"\s+", " ", txt)
        return txt.strip()

    def _rm_leading_parentheses(self, txt):
        """Remove leading parenthesis to break up enclosures like (C - G)"""
        leading_parenthesis_pattern = r"(?<!\S)\((?=[A-G])"
        return re.sub(leading_parenthesis_pattern, "", txt)

    def _rm_symbols(self, txt):
        """Replace multiple whitespace characters with a single space."""
        return re.sub(r"(\[|\]|\{|\}|\*|\||~)", "", txt)

    def _rm_non_chords(self, txt):
        non_chord_pattern = r"(?<!\S)(?![A-G])\S+"  # Use custom word boundary
        return re.sub(non_chord_pattern, "", txt)

    # Homogenization ----
    def _homogenize_qualities(self, txt):
        """Apply standardization rules to chord notations for chord qualities."""
        # Convert major 7th chords from "C7M" to "Cmaj7"
        txt = re.sub(r"([A-G][#b]?)7M", r"\1maj7", txt)
        # Convert "m5-" to "dim"
        txt = re.sub(r"m5-", "dim", txt)
        # Convert "°" to "dim"
        txt = re.sub(r"°", "dim", txt)
        # Convert "-" to "dim" after a 5 or an uppercase letter
        txt = re.sub(r"([A-G][#b]?)-", r"\1dim", txt)
        txt = re.sub(r"5-", "dim", txt)
        # Convert "+" to "aug" if it comes after an uppercase letter
        txt = re.sub(r"([A-G][#b]?)\+", r"\1aug", txt)
        # Convert "+" to "#" if it comes after a number
        txt = re.sub(r"([0-9])(\+)", r"\1#", txt)
        # Convert "-" to "b" after any number that is not 5
        txt = re.sub(r"([0-9])(-)(?![0-9])", r"\1b", txt)
        # Remove no3 and no5 qaulities
        txt = re.sub(r"\(?no[357]{1}\)?", "", txt)
        # Convert minor triads from "Cmin" to "Cm"
        txt = re.sub(r"([A-G][#b]?)min\b", r"\1m", txt)

        # TODO:
        # What about those? F#7(b9/b13)
        # Convert major chords from "C" to "Cmaj" when not followed by other chord symbols
        # txt = re.sub(r"\b([A-G][#b]?)(?![0-9a-zA-Z])", r"\1maj", txt)

        return txt

    def _homogenize_second_extensions(self, txt):
        """
        Standardize chord notation with double extensions by placing all of them in parentheses.
        Some example:
            - A7add13 is converted to A7(13)
            - C7/13 is converted to C7(13)
            - C6/9 is converted to C6(9), which is not common but avoids issues with identification of slash chords
        """
        # Convert slash notation to parenthesis notation
        slash_pattern = r"([A-G]{1}[#b]?[Majmdinsu]{0,3}\d{1,2})/(\d{1,2})"
        txt = re.sub(slash_pattern, r"\1(\2)", txt)
        # Convert add notation to parenthesis notation
        add_pattern = r"([A-G]{1}[#b]?[Majmdinsu]{0,3}\d{1,2})add(\d{1,2})"
        txt = re.sub(add_pattern, r"\1(\2)", txt)
        return txt

    # Selection ----
    def _negative_selection(self, chord_series):
        """
        Filters the input text by removing words that appear a number of times
        less than or equal to a predefined freq_threshold.

        This method counts the occurrences of each word in the input text,
        filters out the words that are below a freq_threshold (default = None), and then
        removes those words from the text.

        Args:
            chord_series (pd.Series): A pandas Series containing text data where
                             each entry is a string to be processed.

        Returns:
            pd.Series: A new Series with filtered text entries where words
                        that appeared equal to or below the freq_threshold have
                        been removed.
        """
        if self.freq_threshold is None:
            return chord_series

        word_count = chord_series.str.split(" ").explode().value_counts()
        # Sets have O(1) lookup time
        rare_words = set(word_count[word_count <= self.freq_threshold].index)

        def filter_rare_words(txt):
            words = txt.split()
            filtered_words = [word for word in words if word not in rare_words]
            return " ".join(filtered_words)

        chord_series = chord_series.apply(filter_rare_words)
        return chord_series

    def _positive_selection(self, txt):
        """Extract and filter valid chord notations from the given text."""
        # Anatomy of a chord
        root = "[A-G]{1}"
        accidental = "[#b]?"
        quality = "[AIJMMNaijmn]{0,3}"
        # quality = r"(?:maj|min|dim|aug|sus|add|m|M)?"
        extension = r"(?:2|4|5|6|7|9|10|11|13)?"
        modifier = r"(?:[ADGIMNOSUadgimnosu]{0,3}[24]?)?"
        extension_2 = rf"(?:\((?:{accidental}{extension},?\s*){{1,2}}\))?"
        slash = rf"(?:\/{root}{accidental})?"
        chord_anatomy = rf"{root}{accidental}{quality}{extension}{modifier}{extension_2}{slash}"

        # Make sure chords appear as standalone tokens and not embedded inside words
        # Example: "Bridge" becomes "B"
        true_chords = rf"(?<![A-Za-z])({chord_anatomy})(?![A-Za-z])"

        chords = re.findall(true_chords, txt)
        return " ".join(chords)

    def clean(self, chord_series):
        chord_series = chord_series.apply(self._split_strings)
        chord_series = chord_series.apply(self._rm_leading_parentheses)
        chord_series = chord_series.apply(self._rm_long_words)
        chord_series = chord_series.apply(self._rm_tab_notation)
        chord_series = chord_series.apply(self._rm_non_chords)
        chord_series = chord_series.apply(self._rm_whitespace)
        # TODO: needed? chord_series = chord_series.apply(self._rm_symbols)
        return chord_series

    def homogenize(self, chord_series):
        chord_series = chord_series.apply(self._homogenize_qualities)
        chord_series = chord_series.apply(self._homogenize_second_extensions)
        return chord_series

    def select(self, chord_series):
        chord_series = self._negative_selection(chord_series)
        chord_series = chord_series.apply(self._positive_selection)
        return chord_series


# TODO: Add logging for debugging
class ChordIsolator:
    """
    Lenient chord detection:
    Tokenization, minimal normalization and rough selection of tokens based on chord structure.
    """

    def __init__(self, char_threshold=20):
        self.char_threshold = char_threshold
        self._cached_tokens = {}
        self._chord_regex = self._init_chord_regex()

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

    SPLIT_REGEX = re.compile(
        r"""
        \([^)]*\)
        |sus(?:2|4)
        |add(?:2|4|5|6|7|9|11|13){1}[#b+-]?
        |maj|7M|M7
        |dim
        |aug|\+
        |m|min
        |[#b]?(?:2|4|5|6|7|9|11|13){1}[+-]?
    """,
        re.VERBOSE,
    )

    MAJOR_TRIAD_REGEX = re.compile(r"(M|Maj|maj)$")

    ALLOWED_QUALITIES = {
        "min": "m",
        "m": "m",
        "-": "m",
        "maj": "maj",
        # "Maj": "",
        # "M": "maj7",
        # TODO: should 7th chords be handled in extensions?
        # "maj7": "maj7",
        "7M": "maj7",
        "M7": "maj7",
        "dim": "dim",
        "aug": "aug",
        "+": "aug",
        "7+": "aug7",
        "5+": "aug5",  # TODO: Wise?
        "sus": "sus4",
        "sus4": "sus4",
        "sus2": "sus2",
    }

    # TODO: only accept accidentals at the end! Leading accidentals are not allowed currently
    EXTENSIONS_REGEX = re.compile(r"(?:2|4|5|6|7|9|11|13){1}[#b+-]?")

    def __init__(self):
        self._cached_chords = {}

    # Public Method ----
    def canonicalize(self, txt: str):
        chords = txt.split(" ")
        chords_cleaned = []

        for chord in chords:
            print(f"chord: {chord} -----------------------")
            if chord in self._cached_chords:
                if self._cached_chords[chord]:
                    chords_cleaned.append(chord)
                    continue

            # Canonization
            raw_decomposed_chord = self._decompose(chord)
            print(f"raw_decomposed_chord : {raw_decomposed_chord}")
            norm_decomposed_chord = self._normalize(raw_decomposed_chord)
            chord_cleaned = self._reconstruct(norm_decomposed_chord)

            if not chord_cleaned:
                self._cached_chords[chord] = False
                chords_cleaned.append("X")
                continue
            else:
                self._cached_chords[chord_cleaned] = True
            print(f"END chord: {chord} -----------------------")
            chords_cleaned.append(chord_cleaned)

        print(self._cached_chords)
        return chords_cleaned

    # Private Methods ----
    def _decompose(self, chord: str) -> dict:
        decomp_chord = {
            "root": None,
            "quality": None,
            "extensions": [],
            "adds": [],
            "sus": None,
            "alterations": [],
            "slash": None,
            "unclear": [],
        }

        chord = chord.replace("(", "").replace(")", "")

        # TODO: Could be more elegant
        tokens = []

        # Slash handling
        if "/" in chord:
            parts = chord.split("/")

            chord = parts[0]

            slash_bass_candidate = parts[-1]

            if self.ROOT_REGEX.match(slash_bass_candidate):
                decomp_chord["slash"] = slash_bass_candidate
            else:
                # decomp_chord["adds"].append(slash_bass_candidate)
                tokens.append(slash_bass_candidate)
                print(f"Line 428: {tokens}")

        # Root handling
        root_capture = self.ROOT_REGEX.match(chord)

        if not root_capture:
            return decomp_chord

        root = root_capture.group(0)
        decomp_chord["root"] = root

        # Modifier handling
        remainder = chord[len(root) :]
        print(f"remainder : {remainder}")

        # TODO: Rethink, not very elegant but fixes disappearing "maj", e.g. Emaj7 stays Emaj7
        if self.MAJOR_TRIAD_REGEX.match(remainder):
            decomp_chord["quality"] = ""
            return decomp_chord

        tokens = tokens + self.SPLIT_REGEX.findall(remainder)
        print(f"tokens : {tokens}")

        for token in tokens:
            token = token.strip()
            print(f"token : {token}")

            if token.startswith("add"):
                print(f"ADD token : {token}")
                decomp_chord["adds"].append(token)

            elif token.startswith("sus"):
                print(f"SUS token : {token}")
                decomp_chord["sus"] = self.ALLOWED_QUALITIES[token]

            elif token in self.ALLOWED_QUALITIES:
                print(f"QUALITIES token : {token}")
                decomp_chord["quality"] = self.ALLOWED_QUALITIES[token]

            # TODO: Still needed?
            elif token.startswith(("#", "b")):
                print(f"ALTERATIONS token : {token}")
                decomp_chord["alterations"].append(token)

            elif self.EXTENSIONS_REGEX.match(token):
                print(f"EXTENSIONS token : {token}")
                decomp_chord["extensions"].append(token)

            # TODO: Remove after testing
            else:
                print(f"unclear token: {token}")
                decomp_chord["unclear"].append(token)

        return decomp_chord

    def _normalize(self, decomp_chord: dict) -> dict:
        # normalize quality default
        if decomp_chord["quality"] is None:
            decomp_chord["quality"] = ""

        # normalize adds vs extensions
        new_adds = []

        for add in decomp_chord["adds"]:
            print(f"Line 467: {decomp_chord['adds']}")
            if add not in decomp_chord["extensions"]:
                print(f"Line 470: {decomp_chord['extensions']}")
                new_adds.append(add)

        decomp_chord["adds"] = sorted(set(new_adds), key=self._num_sort)

        # TODO: normalize sharp or flat extensions!!
        new_extensions = []

        for ext in decomp_chord["extensions"]:
            ext = ext.replace("-", "b").replace("+", "#")
            if "#" in ext or "b" in ext:
                if ext[-1] in "#b":
                    ext = ext[-1] + ext[:-1]

            new_extensions.append(ext)

        # for ext in decomp_chord["extensions"]:
        #     if any(sym in ext for sym in {"-", "+"}):
        #         ext = ext.replace("-", "b").replace("+", "#")
        #     new_extensions.append(ext)

        decomp_chord["extensions"] = sorted(
            set(new_extensions), key=self._num_sort
        )

        decomp_chord["alterations"] = sorted(
            set(decomp_chord["alterations"]), key=self._num_sort
        )

        return decomp_chord

    def _reconstruct(self, decomp_chord: dict) -> str:
        if not decomp_chord["root"]:
            return None

        chord = decomp_chord["root"]

        chord += decomp_chord["quality"]

        if decomp_chord["sus"]:
            chord += decomp_chord["sus"]

        extensions = decomp_chord["extensions"]
        if extensions:
            chord += extensions[0]
            if len(extensions) > 1:
                chord += "(e:" + ",".join(extensions[1:]) + ")"

        modifiers = []
        modifiers.extend(decomp_chord["adds"])
        if modifiers:
            chord += "(m:" + ",".join(modifiers) + ")"

        alterations = []
        alterations.extend(decomp_chord["alterations"])
        if alterations:
            chord += "(a:" + ",".join(alterations) + ")"

        if decomp_chord["slash"]:
            chord += "/" + decomp_chord["slash"]

        unclear = decomp_chord["unclear"]
        if unclear:
            chord += "(u:" + ",".join(unclear) + ")"

        return chord

    def _num_sort(self, x):
        """
        Sort modifiers lists like `["add9", "add2", "add13"]`
        """
        m = re.search(r"\d+", x)

        if m:
            return int(m.group())

        return 999


# TODO: Create UNIT TESTS
cc = ChordCanonizer()

test2 = "C9#11b13 C911+13-"

# test2 = "C7/-9 C7/9-"
# test2 = "Ebmaj7add9/G"
test = "D7(9-)/Eb"
test = "E7/13- E13-"

# Issue with 7ths
test = "Gmaj9 Gmaj7 Gmaj7(9+)"
# Aug tests, too permissive?
test = "C5+ C+5 C7+ Caug C+"

# Extensions vs Add test
test = "A7(13)add9"

test = "Amaj7add9add6(13)"  #  E7(9)(13) E7 Asus2dim A(add9)/E"


res = cc.canonicalize(test2)
print(f"res : {res}")
