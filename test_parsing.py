import pandas as pd
from chordal_wip.chordpipeline import ChordProcessingPipeline
from chordal_wip.chordisolator import ChordIsolator

df = pd.read_csv(
    "hf://datasets/lluccardoner/melodyGPT-song-chords-text-1/melodyGPT-song-chords-text-1.csv"
)
df.to_csv("lluccardoner-melodyGPT-song-chords-text-1.csv")
df = pd.read_csv("lluccardoner-melodyGPT-song-chords-text-1.csv")
df = df[df["chords_str"].notna()]

# ----------------------------------
# Check Raw and Isolator Output ----
# ----------------------------------

# Aim: Investigate raw chords before parsing

# Filter by pop
# df = df[df["genres"].str.contains("pop", case=False)]

tokens = df["chords_str"].str.split().explode().value_counts()
tokens.to_csv("all_tokens.csv")

# ci = ChordIsolator()
# df["isolated"] = df["chords_str"].apply(ci.isolate)
# cnts = df["isolated"].str.split().explode().value_counts()
# cnts = cnts[cnts.index.str.contains(r"\(")]
# cnts.to_csv("test_cnts_wo_exclusion.csv")

# --------------------------------
# Inspect parenthesis content ----
# --------------------------------

# Aim: Identify all separators in parentheses

if False:
    tokens = pd.DataFrame(
        {
            "chords_str": tokens.index,
            "count": tokens.values,
            "chords_str_len": tokens.index.str.len(),
        }
    )

    # Root + parentheses = 3 letters
    tokens = tokens.loc[tokens["chords_str_len"] >= 6]
    tokens = tokens[tokens["chords_str"].str.contains(r"\(", na=False)]
    tokens.to_csv("all_tokens_parenthesis.csv")
    # Extract parenthesis contains
    parent = tokens.copy()
    parent["chords_str_parent"] = parent["chords_str"].str.extract(
        r"\(([^(]+)\)"
    )
    # .reset_index(drop=True)[0]
    parent_spez = parent[
        parent["chords_str_parent"].str.contains(r"[^a-zA-Z0-9+\-#]", na=False)
    ]
    # Bottomline: "/" seems to be the only issue here
    parent_spez.to_csv("all_tokens_parenthesis_special.csv")
    parent_exploded = (
        parent["chords_str_parent"]
        .dropna()
        .apply(list)
        .explode()
        .value_counts()
    )
    parent_exploded.to_csv("parent_exploded.csv")


# -----------------------
# Test real pipeline ----
# -----------------------

cpp = ChordProcessingPipeline()

df = cpp.process(df, "chords_str", write_cache=False)

# Convert all roots to X and slashes to Y to have a clear overview of the different chord types
df["chords_canonized_simp"] = (
    df["chords_canonized"]
    .str.replace(r"[A-G](?:#|b)?", "X", regex=True)
    .str.replace("/X", "/Y", regex=True)
)

canonized_chord = df["chords_canonized"].str.split().explode().value_counts()
print(f"canonized_chord : {canonized_chord}")
canonized_chord = canonized_chord[
    canonized_chord.index.str.contains(r"\(u:", na=False)
]
print(f"canonized_chord : {canonized_chord}")

canonized_chord.to_csv("test_output.csv")
