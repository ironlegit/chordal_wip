from chorda_wip.chordisolator import ChordIsolator
from chorda_wip.chordcanonizer import ChordCanonizer


class ChordProcessingPipeline:
    def __init__(self:
        self.isolator = isolator
        self.canonizer = canonizer

    def process(self, df, input_column, output_column):
        print("ChordProcessingPipeline: Starting isolation...")
        df["temp_isolated"] = df[input_column].apply(self.isolator.isolate)
        print("ChordProcessingPipeline: Isolation complete.")

        print("ChordProcessingPipeline: Starting canonization...")
        df[output_column] = df["temp_isolated"].apply(self.canonizer.canonize)
        df.drop("temp_isolated", axis=1, inplace=True)
        print("ChordProcessingPipeline: Canonization complete.")
        print(f"ChordProcessingPipeline: ✓ Processed {len(df)} rows.")
        return df
