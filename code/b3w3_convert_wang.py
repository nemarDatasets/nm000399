"""c-wang-thal (Dryad doi:10.5061/dryad.zpc866t75; Wang et al. 2022 J Neurosci) -> iEEG-BIDS DERIVATIVE dataset.

Source: 26 DBS<id>_session<n>.mat (v7.3, FieldTrip-like struct D) + contact_info.mat (MNI coordinates).
D.state: 'notch_filt,ds to 1khz,lpf_400, hpf_2, badch detected,badtrial of all type identified, CAR signal at second row,
recording side documented' -> filtered/resampled: this is a derivative, not raw.
D.trial{k,1} = trial k (samples x channels) as preprocessed, NOT re-referenced; D.trial{k,2} = same trial after common
average re-referencing (rows sum to 0). Only column 1 is converted (the CAR version is derivable and stays in sourcedata).
Trials overlap in time (D.time{k} absolute times; consecutive trials share samples), so no continuous signal can be
rebuilt: trials are written back-to-back, one BrainVision segment per trial (vmrk 'New Segment'), and events.tsv gives
each trial's position in the file and its original start time.
Values: float64 -> IEEE_FLOAT_32 (max abs and relative error reported in code/conversion_report.json).
Usage: python b3w3_convert_wang.py <sourcedata_dl> <bids_root>
"""
import hashlib, json, os, re, shutil, sys
import numpy as np, h5py, scipy.io as sio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b3w3_common import wtsv, wjson, write_vhdr, scrub_mat_header, sha256_file

SRC, OUT = sys.argv[1], sys.argv[2]
report = {"sessions": [], "sourcedata": []}
ci = sio.loadmat(os.path.join(SRC, "contact_info.mat"), squeeze_me=True, struct_as_record=False)["contact_info"]
CI = [dict(id=int(c.contact_id), sub=str(c.subject_id), side=str(c.side), ses=[int(x) for x in np.ravel(c.session)], label=str(c.label),
           mni=[float(v) for v in np.ravel(c.mni_coords)]) for c in np.atleast_1d(ci)]
scans = {}
for n in sorted(x for x in os.listdir(SRC) if re.match(r"DBS\d+_session\d+\.mat$", x)):
    sid, ses = re.match(r"(DBS\d+)_session(\d+)\.mat$", n).groups(); ses = int(ses)
    with h5py.File(os.path.join(SRC, n), "r") as hf:
        D = hf["D"]
        s = lambda r: "".join(map(chr, hf[r][()].ravel()))
        fs = float(D["hdr/Fs"][()].ravel()[0])
        labels = [s(r) for r in D["label"][()].ravel()]
        chtype = [s(r) for r in D["hdr/chantype"][()].ravel()]
        chunit = [s(r) for r in D["hdr/chanunit"][()].ravel()]
        side = s(D["side"][()].ravel()[0])
        state = "".join(map(chr, D["state"][()].ravel()))
        def idx(k):
            v = D[k][()]
            return [] if v.dtype == np.uint64 else sorted(int(x) for x in v.ravel())
        flags = {k: set(idx(k)) for k in ("badtrial_final", "codingbad_idx", "quanbad_idx", "visobad_idx", "partialtrial_idx")}
        T = D["trial"][()]; TM = D["time"][()]
        segs, rows, marks, pos = [], [], [], 0
        maxerr, maxrel = 0.0, 0.0
        for k in range(T.shape[0]):
            x = hf[T[k, 0]][()]  # samples x channels
            t = hf[TM[k, 0]][()].ravel()
            assert x.shape[0] == t.size and x.shape[1] == len(labels)
            x32 = x.astype(np.float32)
            e = np.abs(x32.astype(np.float64) - x); maxerr = max(maxerr, float(np.nanmax(e)))
            maxrel = max(maxrel, float(np.nanmax(e / np.maximum(np.abs(x), 1e-12))))
            segs.append(x32)
            i = k + 1
            rows.append([round(pos / fs, 6), round(x.shape[0] / fs, 6), "trial", i, pos, round(float(t[0]), 6), round(float(t[-1]), 6),
                         int(i in flags["badtrial_final"]), int(i in flags["codingbad_idx"]), int(i in flags["quanbad_idx"]),
                         int(i in flags["visobad_idx"]), int(i in flags["partialtrial_idx"])])
            marks.append(("New Segment" if k else "Comment", f"trial {i}", pos, 1))
            pos += x.shape[0]
        starts = [r[5] for r in rows]; ends = [r[6] for r in rows]
        overl = sum(1 for a, b in zip(ends[:-1], starts[1:]) if b <= a)
    sub = f"sub-{sid}"; S = f"ses-{ses}"
    Dd = os.path.join(OUT, sub, S, "ieeg"); os.makedirs(Dd, exist_ok=True)
    stem = f"{sub}_{S}_task-reading"
    data = np.concatenate(segs, axis=0)
    np.ascontiguousarray(data).astype("<f4").tofile(os.path.join(Dd, stem + "_ieeg.eeg"))
    units = ["µV" if u == "uV" else u for u in chunit]
    write_vhdr(os.path.join(Dd, stem + "_ieeg"), len(labels), fs, labels, units, comment=f"b3w3_convert_wang.py: {n} D.trial(:,1) (not CAR) trials back-to-back, float32",
               markers=[m for m in marks if m[0] == "New Segment"])
    wtsv(os.path.join(Dd, stem + "_events.tsv"),
         ["onset", "duration", "trial_type", "trial_index", "sample", "source_time_start", "source_time_end", "badtrial_final", "codingbad", "quanbad", "visobad", "partialtrial"], rows)
    typ = ["DBS" if c == "dbs" else "SEEG" for c in chtype]
    # electrodes for this session
    erows = []
    for lab in labels:
        m = [c for c in CI if c["sub"] == sid and c["label"] == lab and ses in c["ses"]]
        if len(m) == 1:
            c = m[0]; erows.append([lab, "%.6f" % c["mni"][0], "%.6f" % c["mni"][1], "%.6f" % c["mni"][2], "n/a", {"left": "L", "right": "R"}.get(c["side"], "n/a"), c["id"]])
        else:
            erows.append([lab, "n/a", "n/a", "n/a", "n/a", "n/a", "n/a"])
    wtsv(os.path.join(Dd, f"{sub}_{S}_space-MNI152NLin2009bAsym_electrodes.tsv"), ["name", "x", "y", "z", "size", "hemisphere", "contact_id"], erows)
    wjson(os.path.join(Dd, f"{sub}_{S}_space-MNI152NLin2009bAsym_electrodes.json"), {
        "hemisphere": {"Description": "Side as given in contact_info.mat (field 'side': left/right)", "Levels": {"L": "left", "R": "right"}},
        "contact_id": {"Description": "contact_id in contact_info.mat"}})
    wjson(os.path.join(Dd, f"{sub}_{S}_space-MNI152NLin2009bAsym_coordsystem.json"), {
        "iEEGCoordinateSystem": "MNI152NLin2009bAsym", "iEEGCoordinateUnits": "mm",
        "iEEGCoordinateSystemDescription": "MNI ICBM152 NLIN 2009b: the article normalised pre/post-operative images into this space with Lead-DBS; coordinates from contact_info.mat (field mni_coords)",
        "iEEGCoordinateProcessingDescription": "Lead-DBS semi-automatic electrode reconstruction (article, Methods); values copied from contact_info.mat"})
    nchan = {t: typ.count(t) for t in set(typ)}
    rows_c = [[lab, t, u, 2.0, 400.0, fs, re.sub(r"_\d+$|_[a-z]$", "", lab), "good", "n/a",
               ("DBS lead contact (Medtronic 3387 per the article)" if t == "DBS" else "macroelectrode ring of a microelectrode mapping track (macro_a/c/p/m = anterior/central/posterior/medial track per naming; not defined in the release)")]
              for lab, t, u in zip(labels, typ, units)]
    wtsv(os.path.join(Dd, stem + "_channels.tsv"), ["name", "type", "units", "low_cutoff", "high_cutoff", "sampling_frequency", "group", "status", "status_description", "description"], rows_c)
    wjson(os.path.join(Dd, stem + "_ieeg.json"), {
        "TaskName": "reading",
        "TaskDescription": "Reading aloud single consonant-vowel-consonant words and nonwords shown on a screen during awake DBS surgery (120 trials per session; the first 60 alternate unique words and nonwords, the last 60 repeat the nonwords; article). The release contains no per-trial stimulus, lexicality or speech-timing labels.",
        "SamplingFrequency": fs, "PowerLineFrequency": 60,
        "SoftwareFilters": {"AuthorsPreprocessing": {"Description": "D.state: " + state + " (notch at 60 Hz and harmonics, resampled to 1 kHz, low-pass 400 Hz, high-pass 2 Hz per the article)"}},
        "HardwareFilters": "n/a",
        "iEEGReference": "Not re-referenced (column 1 of D.trial); the common-average-referenced copy (column 2) is in sourcedata only. Original recording reference not stated in the release.",
        "RecordingType": "epoched",
        "RecordingDuration": data.shape[0] / fs,
        "DBSChannelCount": nchan.get("DBS", 0), "SEEGChannelCount": nchan.get("SEEG", 0), "ECOGChannelCount": 0,
        "ElectricalStimulation": False,
    })
    scans.setdefault(sub, []).append([f"{S}/ieeg/{stem}_ieeg.vhdr", "n/a"])
    import mne
    rr = mne.io.read_raw_brainvision(os.path.join(Dd, stem + "_ieeg.vhdr"), preload=False, verbose="error")
    k = min(2000, data.shape[0])
    rt = bool(rr.n_times == data.shape[0] and rr.ch_names == labels and np.allclose(rr.get_data(start=0, stop=k) * 1e6, data[:k].T, rtol=1e-6, atol=1e-6))
    report["sessions"].append(dict(file=n, sub=sid, ses=ses, side=side, labels=labels, n_trials=len(rows), samples=int(data.shape[0]),
                                   overlapping_consecutive_trials=overl, float32_max_abs_err=maxerr, float32_max_rel_err=maxrel,
                                   electrodes_matched=sum(1 for r in erows if r[1] != "n/a"), roundtrip_ok=rt))
    print(stem, len(labels), len(rows), data.shape, "overlap", overl, "err", maxerr, "elec", report["sessions"][-1]["electrodes_matched"], "rt", rt, flush=True)
for sub, r in scans.items():
    wtsv(os.path.join(OUT, sub, f"{sub}_scans.tsv"), ["filename", "acq_time"], sorted(r))
SD = os.path.join(OUT, "sourcedata", "dryad-zpc866t75-deidentified"); os.makedirs(SD, exist_ok=True)
for f in sorted(os.listdir(SRC)):
    if f == "SHA256SUMS":
        continue
    b = open(os.path.join(SRC, f), "rb").read()
    nb, ch = scrub_mat_header(b)
    open(os.path.join(SD, f), "wb").write(nb)
    report["sourcedata"].append([f, len(b), hashlib.sha256(b).hexdigest(), hashlib.sha256(nb).hexdigest(), "MAT text header date -> Mmm 01 yyyy" if ch else "unchanged"])
wtsv(os.path.join(SD, "DEIDENTIFICATION_MANIFEST.tsv"), ["path", "bytes_original", "sha256_original", "sha256_here", "change"], report["sourcedata"])
os.makedirs(os.path.join(OUT, "code"), exist_ok=True)
for f in (__file__, os.path.join(os.path.dirname(os.path.abspath(__file__)), "b3w3_common.py")):
    shutil.copy(f, os.path.join(OUT, "code", os.path.basename(f)))
json.dump(report, open(os.path.join(OUT, "code", "conversion_report.json"), "w"), indent=1)
print(json.dumps({"sessions": len(report["sessions"]), "trials": sum(s["n_trials"] for s in report["sessions"]),
                  "rt_all": all(s["roundtrip_ok"] for s in report["sessions"]), "max_abs_err": max(s["float32_max_abs_err"] for s in report["sessions"]),
                  "max_rel_err": max(s["float32_max_rel_err"] for s in report["sessions"]),
                  "electrodes_matched": sum(s["electrodes_matched"] for s in report["sessions"]), "channels": sum(len(s["labels"]) for s in report["sessions"])}, indent=1))
print("CONVERT_DONE")
