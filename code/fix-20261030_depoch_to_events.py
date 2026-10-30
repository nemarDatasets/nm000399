"""Add per-trial labels and timings of the source table D.epoch to events.tsv (fix-20261030).

Source: sourcedata/dryad-zpc866t75-deidentified/DBS<id>_session<n>.mat (Dryad doi:10.5061/dryad.zpc866t75, MATLAB
v7.3; HDF5 payload byte-identical to Dryad v1, see DEIDENTIFICATION_MANIFEST.tsv). D.epoch is a MATLAB `table`
(MCOS) with one row per trial (D.trial), in the order of events.tsv (`trial_index` 1..n; asserted below).
Decoded with mat-io 1.0.0 (https://github.com/foreverallama/matio); this table version lacks props.versionSavedFrom,
so its raw properties are converted with matio's `to_dataframe`.

Times in D.epoch are on the authors' recording clock (D.time). events.tsv already gives, per trial, the file onset
and `source_time_start` (= first D.time value of the trial). A clock time t is placed in the file at
    onset + (t - source_time_start)
and must fall inside the trial segment [onset, onset + duration] (2 ms tolerance). Trials are stored back to back, so a
time outside its own segment would point into another trial's samples: such a value is written n/a and counted
(column `timing_note` says which).

Added columns (n/a when the source cell is empty):
  word, phonetic_code, err_cons1, err_vowel, err_cons2, list_item (D.epoch.trial_id),
  stimulus_onset, speech_onset, speech_offset, vowel_onset, vowel_offset   (s, file time)
The free-text columns comment_1/comment_2 and the bookkeeping columns are not copied (they stay in sourcedata).

Usage: python fix-20261030_depoch_to_events.py <bids_root> --tsv <dir with nm000399_<file>_epoch.tsv>
"""
import argparse
import ast
import csv
import glob
import math
import os

TXT = {"word": "word", "phonetic_code": "phoneticCode", "err_cons1": "err_cons1", "err_vowel": "err_vowel",
       "err_cons2": "err_cons2"}
TIMES = {"stimulus_onset": "stimulus_starts", "speech_onset": "onset_word", "speech_offset": "offset_word",
         "vowel_onset": "onset_vowel", "vowel_offset": "offset_vowel"}


def txt(v):
    if v is None:
        return "n/a"
    s = v.strip()
    if s.startswith("["):
        x = ast.literal_eval(s)
        if not x:
            return "n/a"
        assert len(x) == 1, x
        s = str(x[0])
    s = s.replace("\t", " ").replace("\n", " ").strip()
    return s if s else "n/a"


def num(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return math.nan
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--tsv", required=True)
    a = ap.parse_args()
    total = filled = 0
    outside = {}
    for ev in sorted(glob.glob(os.path.join(a.root, "sub-DBS*/ses-*/ieeg/*_task-reading_events.tsv"))):
        sub = os.path.basename(ev).split("_")[0][len("sub-"):]
        ses = os.path.basename(ev).split("_")[1][len("ses-"):]
        tab = list(csv.DictReader(open(os.path.join(a.tsv, f"nm000399_{sub}_session{ses}_epoch.tsv")), delimiter="\t"))
        with open(ev, newline="") as f:
            rows = list(csv.DictReader(f, delimiter="\t"))
            header = list(rows[0].keys())
        assert len(rows) == len(tab), (ev, len(rows), len(tab))
        sf = None
        for i, (r, t) in enumerate(zip(rows, tab)):
            assert int(r["trial_index"]) == i + 1 and int(float(t["id"])) == i + 1, (ev, i)
            assert int(float(t["session_id"])) == int(ses), (ev, i)
            on, dur, t0 = float(r["onset"]), float(r["duration"]), float(r["source_time_start"])
            if sf is None and i + 1 < len(rows):
                pass
            for col, src in TXT.items():
                r[col] = txt(t[src])
            r["list_item"] = str(int(float(t["trial_id"])))
            notes = []
            for col, src in TIMES.items():
                x = num(t[src])
                if math.isnan(x):
                    r[col] = "n/a"
                    continue
                y = on + (x - t0)
                if not (on - 0.002 <= y <= on + dur + 0.002):
                    r[col] = "n/a"
                    notes.append(f"{col} outside segment ({x - t0:.3f} s from segment start)")
                    outside[col] = outside.get(col, 0) + 1
                    continue
                r[col] = f"{y:.6f}"
            r["timing_note"] = "; ".join(notes) if notes else "n/a"
            total += 1
            filled += r["word"] != "n/a"
        new = list(TXT) + ["list_item"] + list(TIMES) + ["timing_note"]
        out = [c for c in header if c not in new] + new
        with open(ev, "w", newline="") as f:
            w = csv.DictWriter(f, out, delimiter="\t", lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    print("trials", total, "with word", filled, "outside segment", outside)


if __name__ == "__main__":
    main()
