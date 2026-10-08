[![DOI](https://img.shields.io/badge/DOI-10.82901%2Fnemar.nm000399-blue)](https://doi.org/10.82901/nemar.nm000399)

# Thalamic LFP during reading aloud of words and nonwords (Wang et al., 2022) - DERIVATIVE

Local field potentials from the ventral lateral thalamus of 11 patients with essential tremor during awake DBS
lead implantation (University of Pittsburgh), recorded while they read aloud consonant-vowel-consonant words and
nonwords. 4 patients: macroelectrode rings of microelectrode mapping tracks (Alpha Omega Neuro Omega); 7 patients:
the implanted DBS lead (Medtronic 3387, Ripple Grapevine), one session after the left lead and one after bilateral
implantation.

THIS IS A DERIVATIVE DATASET. The Dryad release contains the authors' preprocessed, epoched signals, not the raw
recordings: notch-filtered, resampled to 1 kHz, low-pass 400 Hz, high-pass 2 Hz (field D.state of every file).

## Source
- Dryad: Dengyu Wang, Witold J. Lipski, Alan Bush, Anna Chrabaszcz, Christina Dastolfo-Hromack, Michael W. Dickey, Julie A. Fiez, R. Mark Richardson. Thalamic encoding of lexical status is lateralized during reading aloud.
  doi:10.5061/dryad.zpc866t75 (version 1, 2020-11-02). License: CC0 1.0 (Dryad).
- Article: J Neurosci 42(15):3228-3240 (2022), doi:10.1523/JNEUROSCI.1332-21.2022 (PMC8994537); preprint
  doi:10.1101/2020.07.30.229898. Funding from the Dryad record and article.
- All 27 Dryad files were downloaded through the Dryad API and matched the Dryad sha-256 digests and sizes.

## Structure of the release and how it is represented
- One file per subject and session (`DBS<id>_session<n>.mat`) -> `sub-DBS<id>/ses-<n>/ieeg/` (subject labels are the
  release IDs). 26 sessions, 3057 trials.
- Each trial is stored TWICE in the release: `D.trial{k,1}` as preprocessed (no re-referencing) and `D.trial{k,2}`
  after common-average re-referencing (rows sum to zero). Only column 1 is converted here. The re-referenced copy is
  not converted (it is derivable from column 1) and remains in the original files in sourcedata.
- Trials OVERLAP in time: on the authors' clock (`D.time`) most consecutive trials share samples (2969 of the
  consecutive trial pairs overlap). A continuous recording cannot be rebuilt from the release. Trials are therefore
  written back-to-back as segments of one epoched BrainVision file per session (4.86 h of segments in total; the
  union of the covered time is shorter because of the overlap). `events.tsv` gives each trial's segment position, its
  original start/end time on the authors' clock, and membership in the authors' bad-trial lists
  (badtrial_final, codingbad_idx, quanbad_idx, visobad_idx, partialtrial_idx). No trial was removed.
- The release has NO per-trial stimulus identity, lexical status (word/nonword) or speech onset/offset; the article
  states that each session used one of four 120-item lists whose first 60 items alternate words and nonwords and
  whose last 60 repeat the nonwords, but the list order per session is not released.
- Contacts: `macro_a/c/p/m` (mapping-track macro rings) or `dbs_01`..`dbs_08` (DBS lead contacts; 01-04 left,
  05-08 right). Electrode coordinates per session (`space-MNI152NLin2009bAsym_electrodes.tsv`) come from
  contact_info.mat (Lead-DBS, MNI ICBM152 NLIN 2009b per the article); matched for
  117/117 channel-session pairs.
- Values: float64 in the release, written as float32 (max absolute error 0.0036 µV, max relative error 5.96e-08).

## Participants
Cohort (article): 11 right-handed native English speakers, 3 female, aged 53-84 (median 68), essential tremor. The
article's Table 1 (subject numbers 1-11, not the release IDs):
subject 1: 61 M, left, mapping electrodes, 4 sessions; 2: 70 F, right, mapping, 2; 3: 66 M, left, mapping, 2;
4: 75 M, left, mapping, 3; 5: 64 M; 6: 53 M; 7: 67 M; 8: 71 M; 9: 84 F; 10: 73 F; 11: 68 M (5-11: both sides, DBS
leads, 2 sessions). The release does not give the correspondence to its DBS<id> codes and the session counts of the
mapping-electrode subjects do not match one-to-one, so ages and sexes are not assigned per subject (n/a).

## Privacy
Release IDs (DBS4038 ...) are research codes. No names or dates in the data; D.time is a time-of-day-like clock in
seconds without a date. MAT-file text-header creation dates in the sourcedata copies are reduced to month and year
(`DEIDENTIFICATION_MANIFEST.tsv`).

## Additional metadata and localisation (added 2026-10-08)

Compiled after the upload from the article, its supplement and the source deposit (each statement names its source). Text and sidecar metadata only; no data file was changed.

Sources: P = Wang et al. 2022, J Neurosci 42(15):3228-3240, doi:10.1523/JNEUROSCI.1332-21.2022 (PMC8994537); D = Dryad doi:10.5061/dryad.zpc866t75 (files read in Voyager Jobs).

**Recording.** 4 subjects: recorded during subcortical mapping with the Neuro Omega system (Alpha Omega). The macroelectrode ring of the mapping electrodes is stainless steel, 0.55 mm in diameter and 1.4 mm long, 3 mm above the tip. Three electrodes ran in a Ben-Gun array (2 mm spacing; anterior/central/posterior or central/posterior/medial trajectories), with up to four sessions at different depths. Sampled at 44 kHz, band-pass 0.075 Hz-10 kHz. 7 subjects: recorded from Medtronic 3387 DBS leads (4 Pt-Ir contacts, 1.27 mm diameter, 1.5 mm long, 1.5 mm spacing) with the Grapevine Neural Interface Processor (Ripple) at 30 kHz. Session 1 was recorded after the left lead was placed (left contacts only), session 2 after bilateral implantation (both leads) (P, "Electrophysiological recordings"). In D, channel labels are macro_a/macro_c/macro_p/macro_m (mapping-electrode trajectories) or dbs_01..dbs_08 (dbs_01-04 left, dbs_05-08 right per contact_info.mat).

**Reference.** The paper's analysis used a common-average reference (P). The hardware reference is not stated in the paper (n/a).

**Localisation.** Contacts were localised with LEAD-DBS. The post-op scan was coregistered to the pre-op scan with ANTs and normalised to MNI ICBM152 NLIN 2009b, and the electrodes were reconstructed semi-automatically. Contacts were assigned to nuclei of the Ewert et al. 2018 atlas with a 1 mm cut-off: 38/89 sites were in or next to VA/VLa and 51/89 in or next to VLp (P, "Electrode localization", Results). D/contact_info.mat gives the MNI coordinates of all 89 sites. The per-contact Ewert nucleus labels are not in the deposit.

The column `atlas_label_AAL3` of each `*_space-MNI152NLin2009bAsym_electrodes.tsv` is an AAL3 atlas lookup of the MNI coordinates in that file (ieeg-atlas `coord_regions.py`, nearest labelled voxel). It is a derived label, not one given by the authors.
