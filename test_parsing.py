import pandas as pd
from chordal_wip.chordpipeline import ChordProcessingPipeline
from chordal_wip.chordisolator import ChordIsolator

# df = pd.read_csv(
#     "hf://datasets/lluccardoner/melodyGPT-song-chords-text-1/melodyGPT-song-chords-text-1.csv"
# )

df = pd.read_csv("lluccardoner-melodyGPT-song-chords-text-1.csv")
df = df[df["chords_str"].notna()]

# ----------------------------------
# Check Raw and Isolator Output ----
# ----------------------------------

# Filter by pop
# df = df[df["genres"].str.contains("pop", case=False)]

tokens = df["chords_str"].str.split().explode().value_counts()
# all_tokens.to_csv("all_tokens.csv")

ci = ChordIsolator()
df["isolated"] = df["chords_str"].apply(ci.isolate)
cnts = df["isolated"].str.split().explode().value_counts()
# cnts = cnts[cnts.index.str.contains(r"\(")]
# cnts.to_csv("test_cnts_wo_exclusion.csv")

# --------------------------------
# Inspect parenthesis content ----
# --------------------------------

tokens = pd.DataFrame(
    {
        "chords_str": tokens.index,
        "count": tokens.values,
        "chords_str_len": tokens.index.str.len(),
    }
)

print(f"tokens : {tokens}")

# Root + parentheses = 3 letters
tokens = tokens.loc[tokens["chords_str_len"] >= 6]
tokens = tokens[tokens["chords_str"].str.contains(r"\(", na=False)]
tokens.to_csv("all_tokens_parenthesis.csv")

# Extract parenthesis content
parent = (
    tokens["chords_str"].str.extract(r"\(([^(]+)\)").reset_index(drop=True)[0]
)
print(f"parent : {parent}")


parent_exploded = parent.dropna().apply(list).explode().value_counts()
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

canonized_chord.to_csv("test.csv")
