import mirdata
import pandas as pd
from collections import Counter

beatles = mirdata.initialize("beatles", data_home="data/beatles")
beatles.download()

tracks = beatles.load_tracks()
print(f"{len(tracks)} tracks")


def majority_key(key_data) -> tuple[str, str] | None:
    """Longest-annotated local key -> ('tonic', 'mode').
    Songs modulate; a whole-song predictor is only fairly judged
    against the key that dominates the song."""
    durations = Counter()

    # intervals has shape (n, 2): one row [start, end] per key entry.
    # transposes to (2, n) to get all start and end points in separate
    # lists, i.e. [start1 start2 ...] and [end1 end2 ...]
    starts, ends = key_data.intervals.T

    for label, start, end in zip(key_data.keys, starts, ends):
        durations[label] += end - start

    if not durations:
        return None

    return normalize_key_label(durations.most_common(1)[0][0])


KEY_MODE_MAP = {
    "major": "ionian",
    "ionian": "ionian",
    "minor": "aeolian",
    "aeolian": "aeolian",
}

FLAT_TO_SHARP = {
    "Bb": "A#",
    "Eb": "D#",
    "Ab": "G#",
    "Db": "C#",
    "Gb": "F#",
    "Cb": "B",
    "Fb": "E",
}


def normalize_key_label(label: str) -> tuple[str, str]:
    """
    Isophonics key label -> (tonic, mode), canonicalized to sharps.
    EXTEND the variant handling to match what PHASE 1 printed - the point
    of the assert is that an unknown format FAILS LOUDLY instead of
    silently scoring wrong.
    """
    label = label.strip()

    if ":" in label:
        tonic, mode = label.split(":", 1)
    else:
        tonic, mode = label, "major"

    if mode not in KEY_MODE_MAP:
        raise ValueError(f"unsupported key label: {label!r}")

    tonic = FLAT_TO_SHARP.get(tonic, tonic)
    mode = KEY_MODE_MAP[mode]

    return tonic, mode


rows, skipped = [], []

for track_id, t in tracks.items():
    try:
        # Both of these trigger lazy file loading, which can raise
        # (see the B:sus2 validator quirk) - so both live in the try.
        if t.chords is None or t.key is None:
            skipped.append((track_id, "no chords or key annotations"))
            continue
        truth = majority_key(t.key)
    except ValueError as e:
        skipped.append((track_id, str(e)))
        continue

    if truth is None:
        skipped.append((track_id, "no usable key duration"))
        continue

    rows.append(
        {
            "song_id": track_id,
            "title": t.title,
            "chords_raw": " ".join(t.chords.labels),
            "truth_tonic": truth[0],
            "truth_mode": truth[1],
        }
    )

print(f"kept {len(rows)}, skipped {len(skipped)}:")
for track_id, reason in skipped:
    print(f"  {track_id}: {reason}")

benchmark = pd.DataFrame(rows)
print(len(benchmark), "usable tracks")
