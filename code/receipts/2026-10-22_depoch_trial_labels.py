"""Receipt: D.epoch per-trial labels in the 26 source MAT files of nm000399.

Usage: python 2026-10-22_depoch_trial_labels.py <nemar_root> [<dryad_dir>]
"""

import csv
import hashlib
import sys
from pathlib import Path

import h5py
import numpy as np

SRC = "sourcedata/dryad-zpc866t75-deidentified"
TIMES = ["starts", "ends", "stimulus_starts", "onset_word", "offset_word", "onset_vowel", "offset_vowel", "ITI_starts"]
MAT_HEADER_BYTES = 128


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def differing_offsets(a: Path, b: Path) -> tuple[int, int]:
    x, y = np.fromfile(a, np.uint8), np.fromfile(b, np.uint8)
    assert x.size == y.size, f"size differs: {a} {x.size} vs {b} {y.size}"
    diff = np.flatnonzero(x != y)
    return (int(diff.size), int(diff.max()) if diff.size else -1)


def char(f: h5py.File, ref) -> str:
    o = f[ref]
    if o.attrs.get("MATLAB_empty", 0) or o.attrs.get("MATLAB_class") != b"char":
        return ""
    return "".join(map(chr, o[()].ravel(order="F")))


def mcos_props(f: h5py.File) -> tuple[np.ndarray, dict[int, dict[str, int]]]:
    refs = f["#subsystem#/MCOS"][()].ravel()
    blob = f[refs[0]][()].tobytes()

    def u4(a: int, b: int) -> np.ndarray:
        return np.frombuffer(blob[a:b], "<u4")

    nstr, offs = int(u4(4, 8)[0]), u4(8, 40)
    names = [s.decode() for s in blob[40 : offs[0]].split(b"\0")[:nstr]]
    seg4, pos, props = u4(offs[3], offs[4]), 2, [{}]
    while pos < seg4.size:
        n = int(seg4[pos])
        trip = seg4[pos + 1 : pos + 1 + 3 * n].reshape(n, 3)
        assert (trip[:, 1] == 1).all(), f"unexpected MCOS property type: {trip}"
        props.append({names[a - 1]: int(c) + 2 for a, _, c in trip})
        pos += 1 + 3 * n
        pos += pos % 2
    seg3 = u4(offs[2], offs[3]).reshape(-1, 6)[1:]
    return refs, {int(obj): props[int(s4)] for _, _, _, _, s4, obj in seg3}


def read_table(f: h5py.File, name: str) -> tuple[dict, dict]:
    head = f[name][()].ravel()
    assert f[name].attrs["MATLAB_class"] == b"table", f"{name} is not a MATLAB table"
    refs, objs = mcos_props(f)
    p = {k: f[refs[v]] for k, v in objs[int(head[4])].items()}
    varnames = [char(f, r) for r in p["varnames"][()].ravel(order="F")]
    meta = {
        "nrows": int(p["nrows"][()].item()),
        "Description": char(f, p["props"]["Description"].ref),
        **{k: bool(p["props"][k].attrs.get("MATLAB_empty", 0)) for k in ("VariableUnits", "VariableDescriptions")},
    }
    cols = {}
    for v, r in zip(varnames, p["data"][()].ravel(order="F")):
        o = f[r]
        cls = o.attrs["MATLAB_class"].decode()
        cols[v] = (cls, o[()].ravel() if cls == "double" else [char(f, c) for c in o[()].ravel(order="F")])
    return meta, cols


def filled(col: tuple[str, list | np.ndarray]) -> np.ndarray:
    cls, v = col
    return np.isfinite(v) if cls == "double" else np.array([bool(x) for x in v])


def any_filled(cols: dict, prefix: str) -> np.ndarray:
    return np.any([filled(c) for k, c in cols.items() if k.startswith(prefix)], axis=0)


def stats(x: np.ndarray, scale: float = 1.0) -> str:
    x = x[np.isfinite(x)] * scale
    return f"{x.min():.3f} / {np.median(x):.3f} / {x.max():.3f}" if x.size else "n/a"


def main(root: Path, dryad: Path | None) -> None:
    src = root / SRC
    with (src / "DEIDENTIFICATION_MANIFEST.tsv").open() as fh:
        manifest = {r["path"]: r for r in csv.DictReader(fh, delimiter="\t")}
    mats = sorted(src.glob("DBS*_session*.mat"))
    print(f"MAT files found: {len(mats)}\n")
    print(
        "| file | sha256 = manifest sha256_here | Dryad original sha256 = manifest sha256_original | bytes differing (max offset) |"
    )
    print("|---|---|---|---|")
    for m in mats:
        here = sha256(m) == manifest[m.name]["sha256_here"]
        orig, diff = "not checked", "not checked"
        if dryad is not None:
            orig = str(sha256(dryad / m.name) == manifest[m.name]["sha256_original"])
            diff = "{} ({})".format(*differing_offsets(m, dryad / m.name))
        print(f"| {m.name} | {here} | {orig} | {diff} |")

    rows, tot, variables, metas = [], {}, {}, set()
    for m in mats:
        subj, ses = m.stem.split("_session")
        with h5py.File(m, "r") as f:
            meta, cols = read_table(f, "D/epoch")
            metas.add((meta["Description"], meta["VariableUnits"], meta["VariableDescriptions"]))
            for k, (c, _) in cols.items():
                variables.setdefault(k, [set(), 0])
                variables[k][0].add(c)
                variables[k][1] += 1
            fs = float(f["D/hdr/Fs"][()].item())
            times = [f[r][()].ravel() for r in f["D/time"][()].ravel(order="F")]
            n_trial = f["D/trial"].shape[0]
            pidx = f["D/partialtrial_idx"]
            partial = set() if pidx.attrs.get("MATLAB_empty", 0) else set(pidx[()].ravel().astype(int))
        events = root / f"sub-{subj}/ses-{ses}/ieeg/sub-{subj}_ses-{ses}_task-reading_events.tsv"
        with events.open() as fh:
            ev = list(csv.DictReader(fh, delimiter="\t"))
        t = {k: cols[k][1] for k in TIMES}
        t0 = np.array([x[0] for x in times])
        t1 = np.array([x[-1] for x in times])
        fs_time = np.array([(x.size - 1) / (x[-1] - x[0]) for x in times])
        n = meta["nrows"]
        assert n == len(times) == n_trial == len(ev), (
            f"{m.name}: rows {n}, D.time {len(times)}, D.trial {n_trial}, events {len(ev)}"
        )
        tid = cols["trial_id"][1]
        id_ok = (cols["id"][1] == np.arange(1, n + 1)).all() and [int(e["trial_index"]) for e in ev] == list(
            range(1, n + 1)
        )
        tid_ok = (np.diff(tid) > 0).all() and tid.min() >= 1 and tid.max() <= 120
        ses_ok = (cols["session_id"][1] == int(ses)).all()
        ev_start = np.array([float(e["source_time_start"]) for e in ev])
        ends_off = np.flatnonzero(np.abs(t["ends"] - t1) > 1 / fs) + 1
        order = (
            (t["starts"] < t["stimulus_starts"])
            & (t["stimulus_starts"] < t["onset_word"])
            & (t["onset_word"] < t["offset_word"])
            & (t["offset_word"] <= t["ends"])
        )
        r = {
            "file": m.name,
            "trials": n,
            "id = 1..n = events trial_index": bool(id_ok),
            "trial_id increasing within 1..120": bool(tid_ok),
            "session_id = file session": bool(ses_ok),
            "Fs from D.time span (Hz)": stats(fs_time),
            "max abs(starts - D.time first) (ms)": f"{np.abs(t['starts'] - t0).max() * 1e3:.3f}",
            "max abs(starts - events source_time_start) (ms)": f"{np.abs(t['starts'] - ev_start).max() * 1e3:.3f}",
            "trials with abs(ends - D.time last) > 1 sample": f"{ends_off.size} (all in partialtrial_idx: {set(ends_off) <= partial})",
            "stimulus_starts - starts (s) min/med/max": stats(t["stimulus_starts"] - t["starts"]),
            "ends - offset_word (s) min/med/max": stats(t["ends"] - t["offset_word"]),
            "onset_word - stimulus_starts (s) min/med/max": stats(t["onset_word"] - t["stimulus_starts"]),
            "offset_word - onset_word (s) min/med/max": stats(t["offset_word"] - t["onset_word"]),
            "starts<stim<onset_word<offset_word<=ends": int(order.sum()),
            **{f"{k} finite": int(np.isfinite(t[k]).sum()) for k in TIMES},
            "word non-empty": int(filled(cols["word"]).sum()),
            "phoneticCode non-empty": int(filled(cols["phoneticCode"]).sum()),
            "any err_* filled": int(any_filled(cols, "err_").sum()),
            "any comment* filled": int(any_filled(cols, "comment").sum()),
        }
        rows.append(r)
        for k, v in r.items():
            if isinstance(v, (int, np.integer)) and not isinstance(v, bool):
                tot[k] = tot.get(k, 0) + int(v)

    print(f"\nD.epoch (Description, VariableUnits empty, VariableDescriptions empty) across files: {sorted(metas)}")
    print("| variable | MATLAB class | files containing it |\n|---|---|---|")
    for k, (c, n) in variables.items():
        print(f"| {k} | {'/'.join(sorted(c))} | {n} |")
    print()
    keys = list(rows[0])
    split = keys.index("starts<stim<onset_word<offset_word<=ends")
    for part in (keys[2:split], keys[split:]):
        print("| file | trials | " + " | ".join(part) + " |")
        print("|" + "---|" * (len(part) + 2))
        for r in rows:
            print(f"| {r['file']} | {r['trials']} | " + " | ".join(str(r[k]) for k in part) + " |")
        print(f"| **total** | {tot['trials']} | " + " | ".join(str(tot.get(k, "")) for k in part) + " |\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]) if len(sys.argv) > 2 else None)
