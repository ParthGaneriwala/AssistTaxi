"""Write metadata/samples_v3.csv: the frame ranges that are samples of v3.

A frame is a sample when its level-1 surface is taxiway or runway; airborne frames
are not samples (the videos still ship whole). Surfaces come from
metadata/surface_segments.csv, which is reviewed for one reference camera per run.
Concurrent cameras reuse the reference ranges, shifted by the difference in
recording start time (camera clocks, seconds). Frames a shifted range does not
cover are left out.
Usage: python tools/make_samples.py   (run after tools/make_manifest.py)
"""
import csv, re

# (camera, video) -> (reference video_id, start offset in s = camera start - reference start)
CONCURRENT = {
    **{f"r1-left-{v}": (f"r1-center-{c}", o) for v, c, o in [
        ("GX010007", "GX010001", -9), ("GX010008", "GX010002", -6), ("GX010009-006", "GX010003-007", -4),
        ("GX010010", "GX010004", 5), ("GX010011", "GX010005", -4), ("GX010012-010", "GX010006-001", 5),
        ("GX010013-008", "GX010007", -5)]},
    **{f"r1-right-{v}": (f"r1-center-{c}", o) for v, c, o in [
        ("GX010002", "GX010001", -2), ("GX010003", "GX010002", -1), ("GX010004-004", "GX010003-007", -2),
        ("GX010005", "GX010004", 2), ("GX010006", "GX010005", -3), ("GX010007-013", "GX010006-001", 3),
        ("GX010008-009", "GX010007", -2)]},
    "r2-middle-GX010016": ("r2-bottom-GX010009", -12),
    "r2-top-GX010015": ("r2-bottom-GX010009", -4),
}
SURFACES = {"taxiway", "runway"}


def sec(t):
    m, s = re.fullmatch(r"(\d+):(\d\d)", t).groups()
    return int(m) * 60 + int(s)


def main():
    man = {r["video_id"]: r for r in csv.DictReader(open("metadata/manifest_v3.csv", newline=""))}
    segs = {}
    for r in csv.DictReader(open("metadata/surface_segments.csv", newline="")):
        segs.setdefault(r["video_id"], []).append((sec(r["start"]), sec(r["end"]), r["surface"]))
    for vid, (ref, off) in CONCURRENT.items():
        assert vid not in segs, vid
        segs[vid] = [(s - off, e - off, surf) for s, e, surf in segs[ref]]
    missing = set(man) - set(segs)
    assert not missing, f"no surface segments for {sorted(missing)}"
    out = []
    for vid in man:
        fps, n = float(man[vid]["fps"]), int(man[vid]["frame_count"])
        for s, e, surf in segs[vid]:
            if surf not in SURFACES:
                continue
            if e >= n / fps - 1:  # segment ends are whole seconds; the last one runs to the end
                e = n / fps
            a, b = max(0, round(s * fps)), min(n, round(e * fps)) - 1
            if a <= b:
                out.append({"video_id": vid, "first_frame": a, "last_frame": b, "surface": surf})
    with open("metadata/samples_v3.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    tot = {}
    for r in out:
        tot[r["surface"]] = tot.get(r["surface"], 0) + r["last_frame"] - r["first_frame"] + 1
    print(len(out), "ranges;", tot, "; samples", sum(tot.values()))


if __name__ == "__main__":
    main()
