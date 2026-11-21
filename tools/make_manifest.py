"""Write metadata/manifest_v3.csv: one row per video with its factor values.

Frame identifiers are <video_id>-<index:06d> for index in [0, frame_count).
Factor values come from metadata/*.json (v1, v2) and v3 video_stats.csv; the
round-level values below come from the collection record (paper, Table 1).
Usage: python tools/make_manifest.py
"""
import csv, json, os

UNK = "unknown"
ROUNDS = {  # path prefix -> (round code, release, platform, condition, date, time-of-day bin)
    "v1/original_daytime/": ("r0", "v1", "cockpit", "daytime", None, "afternoon"),
    "v2/round1_glare/": ("r1", "v2", "cockpit", "glare", "2024-12-17", "early morning"),
    "v2/round2_vehicle_night/": ("r2", "v2", "vehicle", "night", "2025-04-23", "night"),
    "v3/round3_dusk_night/": ("r3", "v3", "cockpit", None, "2026-02-26", "evening"),
}
V1_FEB_2023 = {"GX010039-003", "GX010042", "GX020031-002"}  # all other v1 videos: 2022-05-19
R3_NIGHT_FROM = 26  # GX010026 onward recorded after civil twilight; earlier ones are dusk
# Round 1 runs after the sun is up (X59 landing and taxi, return to KMLB), all three cameras
R1_DAYTIME = {"center-GX010006-001", "center-GX010007", "left-GX010012-010", "left-GX010013-008",
              "right-GX010007-013", "right-GX010008-009"}


def video_rows():
    for f in sorted(os.listdir("metadata")):
        if f.endswith(".json") and not f.startswith(("index", "schema")):
            d = json.load(open(os.path.join("metadata", f)))
            yield d["file"]["relative_path"], d["video"]["fps"], d["video"]["frame_count"], d["collection"].get("airport")
    for r in csv.DictReader(open("v3/round3_dusk_night/video_stats.csv", newline="")):
        yield r["file"], round(float(r["avg_fps"]), 3), int(r["frame_count_est"]), r["airport"]


def main():
    rows = []
    for path, fps, n, airport in video_rows():
        prefix = next(p for p in ROUNDS if path.startswith(p))
        code, rel, platform, cond, date, tod = ROUNDS[prefix]
        cam, file = path[len(prefix):].split("/")
        vid = file.rsplit(".", 1)[0]
        view = cam.replace("camera-", "").replace("cam-", "")
        if code == "r0":
            date = "2023-02-19" if vid in V1_FEB_2023 else "2022-05-19"
        if code == "r1" and f"{view}-{vid}" in R1_DAYTIME:
            cond = "daytime"
        if code == "r3":
            cond = "night" if int(vid[-3:]) >= R3_NIGHT_FROM else "dusk"
        rows.append({"video_id": f"{code}-{view}-{vid}", "release": rel, "path": path,
                     "airport": airport or UNK, "viewpoint": view, "condition": cond,
                     "platform": platform, "date": date, "time_of_day": tod,
                     "fps": fps, "frame_count": n})
    ids = [r["video_id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate video_id"
    with open("metadata/manifest_v3.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "videos,", sum(r["frame_count"] for r in rows), "frames")


if __name__ == "__main__":
    main()
