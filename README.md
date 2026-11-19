# AssistTaxi

AssistTaxi is a real-world dataset of taxiway and runway imagery for airport surface perception. It is collected at Melbourne Orlando International Airport (KMLB), Grant-Valkaria (X59) and, from v3, X26, from the cockpit of a Piper Cherokee Warrior and from a ground vehicle.

The dataset is released in versions. Each version adds collection rounds to the previous one and never removes or changes earlier samples, so **v3 = v1 + v2 + the v3 round**.

## Repository layout

```
v1/  original_daytime/            Original round, cockpit, daytime      (introduced in v1)
       camera-center/ camera-left/ camera-right/   videos  -> Zenodo
       raw_data/ annotations/ annotated_data/      extracted frames and labels (vid_1, vid_5)
v2/  round1_glare/                Round 1, cockpit, early-morning glare (introduced in v2)
       camera-center/ camera-left/ camera-right/   videos  -> Zenodo
     round2_vehicle_night/        Round 2, ground vehicle, night        (introduced in v2)
       camera-bottom/ camera-center/ camera-top/   videos  -> Zenodo
       samples/                                    100 sharpest frames (tools/extract.py)
v3/  round3_dusk_night/           Round 3, cockpit, dusk to night       (introduced in v3)
       camera-center/                              videos  -> Zenodo (single camera)
       frame_examples/  video_stats.csv            one middle frame per video; per-video stats
metadata/                         one JSON record per video + index.json
tools/                            extract.py (sharpest-frame extraction), video_stats.py
docs/                             car_setup.jpg (vehicle mount), instances/ (example frames)
```

Video files (`*.MP4`) are not stored in git, because GitHub rejects files larger than 100 MB. They are published on Zenodo; see [Download](#download).

## Collection rounds

| Round | Date | Airports | Platform | Condition | Introduced in | Approx. frames |
|---|---|---|---|---|---|---|
| Original | May 19, 2022; Feb. 19, 2023 | KMLB, X59 | Cockpit | Daytime | v1 | 350,000 |
| Round 1 | Dec. 17, 2024 | KMLB, X59 | Cockpit | Early-morning glare | v2 | 650,000 |
| Round 2 | April 2025 | X59 | Vehicle | Night | v2 | 324,000 |
| Round 3 | Feb. 26, 2026 | KMLB, X59, X26 | Cockpit | Dusk to night | v3 | 530,000 |

Frame counts for Rounds 1 to 3 are estimates derived from recorded duration.

The cockpit rounds before v3 were recorded with three GoPro cameras (left, center, right). Round 3 was recorded with a single center camera. KMLB is a towered airport in Class D airspace, 1.5 miles northwest of downtown Melbourne in Brevard County, Florida. X59 is a non-towered airport in Class G airspace in Grant-Valkaria, Brevard County, Florida.

## Metadata

`metadata/<sample_id>.json` describes one video: file path, frame rate, frame count, resolution, duration, a brightness-based lighting label, motion statistics and quality flags. `metadata/index.json` lists every record. Sample identifiers are persistent and are not changed when files move; only the paths are updated.

Metadata records currently cover v1 and v2. Round 3 (v3) is described by `v3/round3_dusk_night/video_stats.csv` until its JSON records are generated.

## Download

| Version | Content | DOI |
|---|---|---|
| v1.1 | Original round (frames) | [10.5281/zenodo.8144439](https://doi.org/10.5281/zenodo.8144439) |
| v2 | Rounds 1 and 2 (videos) | to be added |
| v3 | Round 3 (videos) | to be added |

## Citation

See `CITATION.cff`.

## License

Apache License 2.0; see `LICENSE`.
