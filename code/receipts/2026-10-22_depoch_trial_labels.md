# Receipt: per-trial labels in the D.epoch tables of the 26 source MAT files

**Claim.** README: per-trial item and speech timing are released (D.epoch) (v1.0.3). For all 3057 trials, `D.epoch` gives the
item (`word`), the stimulus onset (`stimulus_starts`, 2 s after the trial start) and the speech onset/offset
(`onset_word`, `offset_word`); `phoneticCode` is filled in 3044 trials and the articulation-error notes (`err_*`) in 394.
Lexical status is not in the release.

## Source

- Files: the 26 `DBS<id>_session<n>.mat` files (MATLAB v7.3 = HDF5) in
  `sourcedata/dryad-zpc866t75-deidentified/` of this dataset, and the 26 `sub-*/ses-*/ieeg/*_task-reading_events.tsv`.
  NEMAR `origin/main` read: `54b73cf8d9fc291e3774003586ed4db6e967d05f` (shared copy refreshed 2026-10-22; its 26
  events.tsv and `DEIDENTIFICATION_MANIFEST.tsv` are byte-identical to that commit).
- Upstream: Dryad doi:10.5061/dryad.zpc866t75, version 1 (API version 87243, published 2020-11-02), the only version.
  The Dryad v2 API file listing has the 26 MAT files plus `contact_info.mat`, with sha-256 digests and sizes.
- Identification:
  - The git-annex keys (SHA256E) of the 26 MAT files at `54b73cf` equal `sha256_here` in `DEIDENTIFICATION_MANIFEST.tsv`.
  - The manifest's `sha256_original`/`bytes_original` equal the Dryad listing digests/sizes (27/27).
  - Recomputed here (table 1 below): every NEMAR copy hashes to `sha256_here`; every Dryad original, fetched through the
    API for this check and deleted afterwards, hashes to `sha256_original`.
  - Byte comparison: the files differ in 22-23 bytes, all at offsets <= 74, i.e. inside the 116-byte MAT text header
    (creation date reduced to `Mmm 01 yyyy`). The HDF5 payload, D.epoch included, is byte-identical to Dryad v1.
- Scope: the tables are part of the released source (Dryad v1), and they are also distributed by NEMAR in `sourcedata/`.
  They are not converted into `events.tsv`.

## Method

Script: `2026-10-22_depoch_trial_labels.py <nemar_root> <dryad_dir>`. Run on Slurm (job 13447463) with Python 3.12.15,
h5py 3.16.0 (HDF5 2.0.0) and numpy 2.5.4.

- `D.epoch` is a MATLAB `table` object (HDF5 attribute `MATLAB_class = table`). It is decoded from the
  `#subsystem#/MCOS` FileWrapper__ metadata (properties `data`, `nrows`, `varnames`, `props`). Values are read as stored
  (float64 or char cells); no scaling is applied.
- Units: the table's `VariableUnits` and `VariableDescriptions` are empty in all 26 files, so the file does not state units.
  They follow from the clock:
  - `D.hdr.Fs` is 1000 Hz and the span of each `D.time` cell gives 1000.000 Hz in every trial, so `D.time` is in seconds.
  - `starts` equals the first `D.time` sample of the same row within 0.49 ms (less than half a sample), so the time columns
    are in seconds on the authors' `D.time` clock. This is also `events.tsv` `source_time_start` (within 0.49 ms).
- Row alignment:
  - `id` = 1..n = `D.trial`/`D.time` row = `events.tsv` `trial_index`.
  - `trial_id` is strictly increasing within 1..120 (consistent with the position in the session's 120-item list, with gaps).
  - `session_id` = the file's session number.
- Relative timing. Each trial window is [`starts`, `ends`]:
  - `stimulus_starts - starts` and `ends - offset_word` are computed per trial.
  - Order check: `starts < stimulus_starts < onset_word < offset_word <= ends`.
  - Rows whose `ends` differs from the last `D.time` sample by more than one sample are counted, and checked against
    `D.partialtrial_idx`.
  - To place a label in the NEMAR recording: onset in file = `events.tsv` `onset` + (label time - `source_time_start`).
- Coverage counts: finite numeric values and non-empty char cells per column. "any err_* filled" counts trials with any
  of `err_cons1`/`err_vowel`/`err_cons2` non-empty or finite; "any comment* filled" works the same way for the comment columns.

## Result (script output, verbatim)

MAT files found: 26

| file | sha256 = manifest sha256_here | Dryad original sha256 = manifest sha256_original | bytes differing (max offset) |
|---|---|---|---|
| DBS4038_session1.mat | True | True | 23 (74) |
| DBS4038_session2.mat | True | True | 23 (74) |
| DBS4038_session3.mat | True | True | 23 (74) |
| DBS4038_session4.mat | True | True | 23 (74) |
| DBS4040_session1.mat | True | True | 23 (74) |
| DBS4040_session2.mat | True | True | 22 (74) |
| DBS4046_session1.mat | True | True | 23 (74) |
| DBS4046_session2.mat | True | True | 23 (74) |
| DBS4046_session3.mat | True | True | 23 (74) |
| DBS4047_session1.mat | True | True | 23 (74) |
| DBS4047_session2.mat | True | True | 23 (74) |
| DBS4047_session3.mat | True | True | 23 (74) |
| DBS4049_session1.mat | True | True | 23 (74) |
| DBS4049_session2.mat | True | True | 22 (74) |
| DBS4051_session1.mat | True | True | 23 (74) |
| DBS4051_session2.mat | True | True | 23 (74) |
| DBS4052_session1.mat | True | True | 23 (74) |
| DBS4052_session2.mat | True | True | 23 (74) |
| DBS4053_session1.mat | True | True | 22 (74) |
| DBS4053_session2.mat | True | True | 23 (74) |
| DBS4054_session1.mat | True | True | 23 (74) |
| DBS4054_session2.mat | True | True | 23 (74) |
| DBS4055_session1.mat | True | True | 23 (74) |
| DBS4055_session2.mat | True | True | 23 (74) |
| DBS4056_session1.mat | True | True | 23 (74) |
| DBS4056_session2.mat | True | True | 23 (74) |

D.epoch (Description, VariableUnits empty, VariableDescriptions empty) across files: [('coding', True, True)]
| variable | MATLAB class | files containing it |
|---|---|---|
| id | double | 26 |
| starts | double | 26 |
| ends | double | 26 |
| duration | double | 26 |
| phoneticCode | cell | 26 |
| err_cons1 | cell | 26 |
| err_vowel | cell/double | 26 |
| err_cons2 | cell | 26 |
| onset_word | double | 26 |
| offset_word | double | 26 |
| unveil | double | 26 |
| comment_1 | cell | 6 |
| comment_2 | cell/double | 6 |
| onset_vowel | double | 26 |
| offset_vowel | double | 26 |
| word | cell | 26 |
| trial_id | double | 26 |
| session_id | double | 26 |
| ITI_starts | double | 26 |
| stimulus_starts | double | 26 |
| comment | cell | 20 |
| comment_3 | cell | 2 |

| file | trials | id = 1..n = events trial_index | trial_id increasing within 1..120 | session_id = file session | Fs from D.time span (Hz) | max abs(starts - D.time first) (ms) | max abs(starts - events source_time_start) (ms) | trials with abs(ends - D.time last) > 1 sample | stimulus_starts - starts (s) min/med/max | ends - offset_word (s) min/med/max | onset_word - stimulus_starts (s) min/med/max | offset_word - onset_word (s) min/med/max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DBS4038_session1.mat | 120 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.484 | 1 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.519 / 0.590 / 0.815 | 0.333 / 0.592 / 0.889 |
| DBS4038_session2.mat | 118 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.484 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.459 / 0.569 / 0.840 | 0.173 / 0.517 / 0.932 |
| DBS4038_session3.mat | 118 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.484 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.472 / 0.549 / 0.709 | 0.316 / 0.614 / 0.973 |
| DBS4038_session4.mat | 118 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.484 | 1 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.442 / 0.552 / 0.873 | 0.255 / 0.625 / 1.084 |
| DBS4040_session1.mat | 118 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.484 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.894 / 1.423 / 2.609 | 0.420 / 0.738 / 1.295 |
| DBS4040_session2.mat | 116 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.484 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.513 / 1.335 / 11.292 | 0.493 / 0.781 / 1.594 |
| DBS4046_session1.mat | 119 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.484 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.647 / 1.010 / 2.002 | 0.274 / 0.712 / 1.234 |
| DBS4046_session2.mat | 120 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.484 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.592 / 0.816 / 1.636 | 0.419 / 0.739 / 1.218 |
| DBS4046_session3.mat | 117 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.484 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.580 / 0.814 / 1.856 | 0.355 / 0.801 / 1.106 |
| DBS4047_session1.mat | 120 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.484 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.652 / 0.990 / 3.191 | 0.406 / 0.597 / 0.874 |
| DBS4047_session2.mat | 117 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.484 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.635 / 0.908 / 3.190 | 0.335 / 0.527 / 0.844 |
| DBS4047_session3.mat | 114 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.484 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.621 / 0.905 / 2.211 | 0.353 / 0.517 / 0.768 |
| DBS4049_session1.mat | 117 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.484 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.629 / 0.933 / 5.036 | 0.219 / 0.656 / 1.227 |
| DBS4049_session2.mat | 119 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.484 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.539 / 0.893 / 5.708 | 0.319 / 0.711 / 1.309 |
| DBS4051_session1.mat | 119 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.483 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.291 / 0.917 / 4.737 | 0.485 / 0.644 / 1.221 |
| DBS4051_session2.mat | 118 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.483 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.496 / 0.730 / 3.884 | 0.444 / 0.656 / 0.964 |
| DBS4052_session1.mat | 119 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.483 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.608 / 1.180 / 4.599 | 0.358 / 0.678 / 2.453 |
| DBS4052_session2.mat | 114 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.483 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.489 / 0.894 / 3.832 | 0.321 / 0.652 / 2.062 |
| DBS4053_session1.mat | 119 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.483 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.554 / 0.817 / 1.756 | 0.287 / 0.640 / 1.076 |
| DBS4053_session2.mat | 104 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.483 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.638 / 0.914 / 2.747 | 0.322 / 0.557 / 0.905 |
| DBS4054_session1.mat | 120 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.484 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.589 / 1.021 / 1.724 | 0.434 / 0.808 / 1.778 |
| DBS4054_session2.mat | 120 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.484 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.603 / 0.834 / 2.230 | 0.267 / 0.778 / 1.400 |
| DBS4055_session1.mat | 114 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.484 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.837 / 1.574 / 5.389 | 0.359 / 0.756 / 1.874 |
| DBS4055_session2.mat | 119 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.484 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.779 / 1.303 / 4.657 | 0.430 / 0.713 / 1.593 |
| DBS4056_session1.mat | 120 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.483 | 0.483 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.536 / 1.043 / 2.040 | 0.309 / 0.639 / 1.642 |
| DBS4056_session2.mat | 120 | True | True | True | 1000.000 / 1000.000 / 1000.000 | 0.490 | 0.489 | 0 (all in partialtrial_idx: True) | 2.000 / 2.000 / 2.000 | 2.000 / 2.000 / 2.000 | 0.537 / 0.858 / 2.189 | 0.394 / 0.683 / 0.990 |
| **total** | 3057 |  |  |  |  |  |  |  |  |  |  |  |

| file | trials | starts<stim<onset_word<offset_word<=ends | starts finite | ends finite | stimulus_starts finite | onset_word finite | offset_word finite | onset_vowel finite | offset_vowel finite | ITI_starts finite | word non-empty | phoneticCode non-empty | any err_* filled | any comment* filled |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DBS4038_session1.mat | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 118 | 120 | 120 | 119 | 13 | 5 |
| DBS4038_session2.mat | 118 | 118 | 118 | 118 | 118 | 118 | 118 | 118 | 117 | 118 | 118 | 118 | 29 | 13 |
| DBS4038_session3.mat | 118 | 118 | 118 | 118 | 118 | 118 | 118 | 118 | 117 | 118 | 118 | 118 | 8 | 8 |
| DBS4038_session4.mat | 118 | 118 | 118 | 118 | 118 | 118 | 118 | 118 | 118 | 118 | 118 | 118 | 16 | 11 |
| DBS4040_session1.mat | 118 | 118 | 118 | 118 | 118 | 118 | 118 | 118 | 112 | 118 | 118 | 118 | 15 | 9 |
| DBS4040_session2.mat | 116 | 116 | 116 | 116 | 116 | 116 | 116 | 116 | 116 | 116 | 116 | 116 | 4 | 61 |
| DBS4046_session1.mat | 119 | 119 | 119 | 119 | 119 | 119 | 119 | 119 | 119 | 119 | 119 | 118 | 25 | 6 |
| DBS4046_session2.mat | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 20 | 4 |
| DBS4046_session3.mat | 117 | 117 | 117 | 117 | 117 | 117 | 117 | 117 | 116 | 117 | 117 | 117 | 7 | 3 |
| DBS4047_session1.mat | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 119 | 119 | 120 | 120 | 120 | 10 | 6 |
| DBS4047_session2.mat | 117 | 117 | 117 | 117 | 117 | 117 | 117 | 117 | 115 | 117 | 117 | 116 | 11 | 4 |
| DBS4047_session3.mat | 114 | 114 | 114 | 114 | 114 | 114 | 114 | 114 | 114 | 114 | 114 | 113 | 10 | 1 |
| DBS4049_session1.mat | 117 | 117 | 117 | 117 | 117 | 117 | 117 | 117 | 117 | 117 | 117 | 117 | 17 | 25 |
| DBS4049_session2.mat | 119 | 119 | 119 | 119 | 119 | 119 | 119 | 119 | 118 | 119 | 119 | 118 | 21 | 6 |
| DBS4051_session1.mat | 119 | 119 | 119 | 119 | 119 | 119 | 119 | 119 | 118 | 119 | 119 | 119 | 10 | 64 |
| DBS4051_session2.mat | 118 | 118 | 118 | 118 | 118 | 118 | 118 | 118 | 118 | 118 | 118 | 117 | 19 | 10 |
| DBS4052_session1.mat | 119 | 119 | 119 | 119 | 119 | 119 | 119 | 115 | 119 | 119 | 119 | 119 | 32 | 13 |
| DBS4052_session2.mat | 114 | 114 | 114 | 114 | 114 | 114 | 114 | 113 | 114 | 114 | 114 | 114 | 34 | 13 |
| DBS4053_session1.mat | 119 | 119 | 119 | 119 | 119 | 119 | 119 | 119 | 119 | 119 | 119 | 119 | 5 | 33 |
| DBS4053_session2.mat | 104 | 104 | 104 | 104 | 104 | 104 | 104 | 104 | 104 | 104 | 104 | 104 | 1 | 6 |
| DBS4054_session1.mat | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 119 | 119 | 120 | 120 | 120 | 21 | 38 |
| DBS4054_session2.mat | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 119 | 14 | 38 |
| DBS4055_session1.mat | 114 | 114 | 114 | 114 | 114 | 114 | 114 | 114 | 113 | 114 | 114 | 112 | 20 | 35 |
| DBS4055_session2.mat | 119 | 119 | 119 | 119 | 119 | 119 | 119 | 118 | 118 | 119 | 119 | 119 | 14 | 58 |
| DBS4056_session1.mat | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 9 | 13 |
| DBS4056_session2.mat | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 116 | 9 | 23 |
| **total** | 3057 | 3057 | 3057 | 3057 | 3057 | 3057 | 3057 | 3049 | 3038 | 3057 | 3057 | 3044 | 394 | 506 |


Summary:
- Every trial has `word`, `stimulus_starts`, `onset_word` and `offset_word` (3057/3057).
- `stimulus_starts - starts` = 2.000 s and `ends - offset_word` = 2.000 s in every trial. The window is 2 s before the
  stimulus to 2 s after the end of speech.
- The order check holds in 3057/3057 trials.
- `phoneticCode` is non-empty in 3044 trials. The `err_*` notes are filled in 394 trials and empty in the rest.
- In 2 trials, both listed in `D.partialtrial_idx`, the last `D.time` sample differs from `ends` by more than one sample.
- No column gives lexical status.

## Coverage

26 of 26 MAT files, 26 of 26 events.tsv, 3057 of 3057 trials.
