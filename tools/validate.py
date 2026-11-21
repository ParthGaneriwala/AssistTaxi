"""Check a release against the AssistTaxi specification. Prints one line per check and
exits non-zero if any check fails.

  1. video manifest: unique video_id, factor values in the schema, no unknown factor
     on any video that contributes samples
  2. sample manifest: ranges inside each video, non-overlapping, surface in level 1
  3. reference split (if splits/v3 is present): blocks pairwise disjoint, every ID a
     sample, frames of different blocks of one sequence at least GAP frames apart, and
     each concurrency group (run) labeled from one camera only
  4. v1 contour labels unchanged since the v1.1 tag (needs git history)

Usage: python tools/validate.py
"""
import csv, json, os, subprocess, sys
from collections import defaultdict

GAP = 100
results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}{'  ' + detail if detail else ''}")


schema = json.load(open("metadata/schema_v3.json"))
man = list(csv.DictReader(open("metadata/manifest_v3.csv", newline="")))
vids = {r["video_id"]: r for r in man}
check("video IDs unique", len(vids) == len(man), f"{len(man)} videos")
bad = [(r["video_id"], f) for r in man for f in ("airport", "viewpoint", "condition", "platform")
       if r[f] not in schema["factors"][f]["values"] + [schema["unknown_token"]]]
check("factor values in schema", not bad, str(bad[:3]) if bad else "")

samples = defaultdict(list)
for r in csv.DictReader(open("metadata/samples_v3.csv", newline="")):
    samples[r["video_id"]].append((int(r["first_frame"]), int(r["last_frame"]), r["surface"]))
unk = [v for v in samples if any(vids[v][f] == schema["unknown_token"]
                                  for f in ("airport", "viewpoint", "condition", "platform"))]
check("no unknown factor on sampled videos", not unk, str(unk[:3]) if unk else "")
labels = set(schema["semantic_levels"]["1"]["labels"])
probs = []
for v, rs in samples.items():
    n = int(vids[v]["frame_count"])
    rs.sort()
    for i, (a, b, s) in enumerate(rs):
        if not (0 <= a <= b < n) or s.capitalize() not in labels or (i and a <= rs[i - 1][1]):
            probs.append((v, a, b, s))
total = sum(b - a + 1 for rs in samples.values() for a, b, _ in rs)
check("sample ranges valid and disjoint", not probs, f"{total} samples in {len(samples)} videos")

if os.path.isdir("splits/v3"):
    def is_sample(v, i):
        return any(a <= i <= b for a, b, _ in samples.get(v, ()))
    blocks = {}
    for b in ("train", "val", "test"):
        blocks[b] = {}
        for line in open(f"splits/v3/{b}.txt"):
            v, i = line.strip().rsplit("-", 1)
            blocks[b].setdefault(v, set()).add(int(i))
    ids = {b: {(v, i) for v, s in d.items() for i in s} for b, d in blocks.items()}
    check("split blocks pairwise disjoint",
          not (ids["train"] & ids["val"] or ids["train"] & ids["test"] or ids["val"] & ids["test"]),
          " / ".join(f"{b} {len(s)}" for b, s in ids.items()))
    outside = [x for s in ids.values() for x in s if not is_sample(*x)]
    check("every split ID is a sample", not outside, f"{len(outside)} outside" if outside else "")
    near = 0
    for v in {v for d in blocks.values() for v in d}:
        tagged = sorted((i, b) for b, d in blocks.items() for i in d.get(v, ()))
        near += sum(1 for (i, b), (j, c) in zip(tagged, tagged[1:]) if b != c and j - i < GAP)
    check(f"blocks of one sequence separated by >= {GAP} frames", near == 0,
          f"{near} violations" if near else "")
    runs = defaultdict(set)  # concurrency group = round + recording slot; one camera per group
    for v in {v for d in blocks.values() for v in d}:
        runs[v.split("-")[0]].add(v.split("-")[1])
    check("each round's labeled frames come from one camera", all(len(c) == 1 for c in runs.values()),
          ", ".join(f"{r}: {sorted(c)}" for r, c in sorted(runs.items())))

try:
    def blobs(ref, path):
        out = subprocess.run(["git", "ls-tree", "-r", ref, "--", path], capture_output=True, text=True, check=True).stdout
        return {os.path.basename(l.split("\t")[1]): l.split()[2] for l in out.splitlines()}
    old, new = blobs("v1.1", "annotations/vid_5"), blobs("HEAD", "labels/cdlem/v1_5")
    check("v1 contour labels identical to v1.1", old == new and len(old) > 0, f"{len(new)} files")
except Exception as e:
    print(f"SKIP  v1 contour labels identical to v1.1  ({e.__class__.__name__})")

sys.exit(0 if all(results) else 1)
