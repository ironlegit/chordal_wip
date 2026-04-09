import pandas as pd
from chordal_wip.chordpipeline import ChordProcessingPipeline


df = pd.read_csv(
    "hf://datasets/lluccardoner/melodyGPT-song-chords-text-1/melodyGPT-song-chords-text-1.csv"
)
df = df[df["chords_str"].notna()]

cpp = ChordProcessingPipeline()

df = cpp.process(df, "chords_str", write_cache=False)
df.to_csv("canonized_df.csv")
print(df.head())

# TODO:
# 1. Homogenize keys
# 2. Simplify keys to triads
# 3. Predict keys from dataset
# Bonus: Parametrize config
