import pandas as pd

from chordal_wip.chordpipeline import ChordProcessingPipeline
from chordal_wip.key import KeyPredictor

df = pd.read_csv(
    "hf://datasets/lluccardoner/melodyGPT-song-chords-text-1/melodyGPT-song-chords-text-1.csv"
)

df = df[df["genres"].str.contains("pop", case=False)]
df = df.sample(frac=0.2)
df = df[df["chords_str"].notna()]

print(f"df : {df.shape[0]}")

cpp = ChordProcessingPipeline()
kp = KeyPredictor()

df = cpp.process(df, "chords_str", write_cache=False)

df["song_id"] = df["artist_name"].str.cat(df["song_name"], sep="-")

result = kp.predict_all(df.set_index("song_id")["chords_simplified"])

result.to_parquet("key_predictions.parquet")  # cheap durable checkpoint

# the views you'll actually use:
result["top2_relation"].value_counts()  # how benign are the ambiguities?
result["margin"].describe()  # where would you cut?
result["oov_fraction"].describe()  # is the triad simplification working?
print(result)
exit()
df.to_csv("canonized_df.csv")

# TODO:
# 1. Find dataset with keys to evaluate if predicting works correctly
