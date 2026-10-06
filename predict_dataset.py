import pandas as pd
from chordal_wip.chordpipeline import ChordProcessingPipeline


df = pd.read_csv(
    "hf://datasets/lluccardoner/melodyGPT-song-chords-text-1/melodyGPT-song-chords-text-1.csv"
)

df = df[df["genres"].str.contains("pop", case=False)]
df = df.sample(frac=0.2)
print(df)
exit()
print(f"df : {df.shape[0]}")
df = df[df["chords_str"].notna()]
print(f"df : {df.shape[0]}")

cpp = ChordProcessingPipeline()


df = cpp.process(df, "chords_str", write_cache=False)
df.to_csv("canonized_df.csv")

# TODO:
# 1. Find dataset with keys to evaluate if predicting works correctly
