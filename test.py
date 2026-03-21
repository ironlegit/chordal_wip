from datasets import load_dataset
import pandas as pd
import re
from chordal_wip.chordisolator import ChordIsolator
from chordal_wip.chordcanonizer import ChordCanonizer

ci = ChordIsolator()
cc = ChordCanonizer()

ds = load_dataset("lluccardoner/melodyGPT-song-chords-text-1")

ds = ds["train"].to_pandas()

ds = ds[ds["chords_str"].notna()]

# Filter by pop
# ds_pop = ds[ds["genres"].str.contains("jazz", case=False)]

print("head")

ds["chords_str_clean"] = ds["chords_str"].apply(ci.raw_chord_isolation)
ds["chords_str_canonized"] = ds["chords_str_clean"].apply(cc.canonicalize)

print(ds.head())
exit
# ds["chords_str_clean"] = ds["chords_str"].str.split().explode().value_counts()
# # cnts = cnts[cnts.index.str.contains("[+-]+")]
# cnts_before = cnts[cnts.index.str.contains("[#b+-]{1}(2|4|6|7|9|11|13){1}")]
# cnts_before = cnts_before[cnts_before.index.str.len() > 4]
#
# cnts_after = cnts[cnts.index.str.contains("(2|4|6|7|9|11|13){1}[#b+-]{1}")]
# cnts_after = cnts_after[cnts_after.index.str.len() > 4]
#
# cnts_before.to_csv("test_cnts_before.csv")
# cnts_after.to_csv("test_cnts_after.csv")
#
#
# exit()
# # TODO: Move into ChordCleaner
# unique_words = ds["chords_str_clean"].str.split().explode().drop_duplicates()
# word_length_df = unique_words.reset_index(drop=True).to_frame()
# word_length_df["length"] = word_length_df["chords_str_clean"].str.len()
# word_length_df.to_csv("test_cnt_len.csv")
# exit()
# cnts = ds["chords_str_clean"].str.split().explode().value_counts()
# print(len(ds["chords_str_clean"].str.split().explode()))
#
# # cnts.to_csv("test_cnts.csv", header=True)
#
# #
# # ds_pop["chords_str_clean"] = cc.clean(series)
# # print(f"nrow: {series.shape[0]}")
# #
# #
# # ds_pop.iloc[0:1000].to_csv("test.csv")
