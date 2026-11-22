# AssistTaxi

AssistTaxi is a real-world dataset of taxiway and runway imagery for airport surface perception. It is collected at Melbourne Orlando International Airport (KMLB), Grant-Valkaria (X59) and, from v3, Sebastian Municipal (X26), from the cockpit of a Piper Cherokee Warrior and from a ground vehicle.

The dataset is released in versions. Each version adds collection rounds to the previous one and never removes or changes earlier samples, so **v3 = v1 + v2 + the v3 round**.

## Repository layout

```
AssistTaxi/
├── v1/
│   └── original_daytime/
│       ├── camera-center/
│       ├── camera-left/
│       ├── camera-right/
│       └── video_stats.csv
├── v2/
│   ├── round1_glare/
│   │   ├── camera-center/
│   │   ├── camera-left/
│   │   ├── camera-right/
│   │   └── video_stats.csv
│   └── round2_vehicle_night/
│       ├── camera-bottom/
│       ├── camera-middle/
│       ├── camera-top/
│       └── video_stats.csv
├── v3/
│   └── round3_dusk_night/
│       ├── camera-center/
│       └── video_stats.csv
├── metadata/
│   ├── schema_v3.json
│   ├── manifest_v3.csv
│   ├── samples_v3.csv
│   ├── frame_examples_v3.txt
│   └── surface_segments.csv
├── labels/
│   └── cdlem/v1_5/
├── tools/
│   ├── extract.py
│   ├── video_stats.py
│   ├── make_manifest.py
│   ├── make_samples.py
│   ├── make_image_list.py
│   └── validate.py
└── docs/
    ├── car_setup.jpg
    └── instances/
```

Each release contains one example frame per video under `*/frame_examples/`, named by sample ID. Videos (`*.MP4`) are published on Zenodo (see [Download](#download)); only example frames and metadata are stored in this repository. Use `tools/extract.py` to reproduce extracted frames from the videos.

## Collection rounds

| Round | Date | Airports | Platform | Condition | Introduced in | Frames |
|---|---|---|---|---|---|---|
| Original | May 19, 2022; Feb. 19, 2023 | KMLB, X59 | Cockpit | Daytime | v1 | 370,881 |
| Round 1 | Dec. 17, 2024 | KMLB, X59 | Cockpit | Early-morning glare | v2 | 676,194 |
| Round 2 | Apr. 23, 2025 | X59 | Vehicle | Night | v2 | 651,484 |
| Round 3 | Feb. 26, 2026 | KMLB, X59, X26 | Cockpit | Dusk to night | v3 | 530,247 |

The frame counts above are the decoded-frame totals in `metadata/manifest_v3.csv`. Each value sums `frame_count` across all videos in that round.

The cockpit rounds before v3 were recorded with three GoPro cameras (left, center, right) and Round 2 with three cameras on the vehicle (bottom, middle, top). Round 3 was recorded with a single center camera. KMLB is a towered airport in Class D airspace, 1.5 miles northwest of downtown Melbourne in Brevard County, Florida. X59 is a non-towered airport in Class G airspace in Grant-Valkaria, Brevard County, Florida. X26 (Sebastian Municipal) is a non-towered general aviation airport in Class G airspace in Sebastian, Indian River County, Florida.

## Metadata

| File | Content |
|---|---|
| `metadata/schema_v3.json` | Release schema: metadata factors and their values, annotation modalities, the semantic level (Taxiway, Runway), the unknown token and the sample ID format. |
| `metadata/manifest_v3.csv` | One row per video: `video_id`, release, path, airport, viewpoint, condition, platform, date, time of day, frame rate and frame count. |
| `metadata/samples_v3.csv` | The frames that are samples: `video_id`, first and last frame, and surface (taxiway or runway). |
| `metadata/surface_segments.csv` | Taxiway, runway and airborne time ranges, reviewed for one reference camera per run; `samples_v3.csv` is derived from it. |
| `metadata/<name>.json`, `index.json` | Per-video technical records for v1 and v2 (stream properties, brightness, quality flags, airport). |
| `<round>/video_stats.csv` | Per-video stream statistics (codec, resolution, frame rate, duration, frame count), airport and example frame, one file per round (`tools/video_stats.py`). |

**Sample IDs** are `<video_id>-<frame index>`, for example `r1-center-GX010001-000123`, where `video_id` is `<round>-<viewpoint>-<video>` (rounds `r0` original, `r1`, `r2`, `r3`) and the frame index counts decoded frames from 0. A frame is a sample when it shows a taxiway or a runway; frames recorded in the air are part of the videos but are not samples. Concurrent cameras of one run share the surface ranges of the reference camera, shifted by the difference in recording start time. Identifiers are persistent: later releases add samples and fields but do not rename or remove them.

To regenerate the manifests after editing the metadata:

```
python tools/make_manifest.py
python tools/make_samples.py
```

`metadata/frame_examples_v3.txt` provides a standardized, one-relative-path-per-line
manifest for the example frames stored in this repository.

After downloading and extracting the full videos, generate a manifest containing
every sampled frame:

```
python tools/make_image_list.py --output metadata/image_list_v3.txt
```

Use `--images-root <directory>` when extracted frames are outside the repository.
The generated paths are `--images-root/<video_id>-<frame index>.jpg`, and the
command can be restricted with `--release`, `--airport`, `--viewpoint`, or
`--surface`.

`python tools/validate.py` checks a release against the specification: unique identifiers, factor values in the schema with no unknowns on sampled videos, disjoint sample ranges within each video, and, where the reference split is present, disjoint blocks that contain only samples, guard intervals between blocks and one labeled camera per run. It also checks that the v1 contour labels are unchanged since the v1.1 tag.

## Extracting frames

```
python tools/extract.py <video.MP4> <out_dir> --video-id <video_id> [--samples metadata/samples_v3.csv]
```

writes `<video_id>-<frame index>.jpg`, matching the sample IDs; `--samples` keeps only frames that are samples. Without `--video-id`, the script keeps the 100 sharpest frames of the video. Use `--top <n>` to change that default.

## Annotations and reference split

Three labeling procedures have been applied to AssistTaxi imagery, and each is kept as its own modality:

- **CDLEM** (contour detection and line extraction), introduced with v1 [1]. The polylines for video 5 are in `labels/cdlem/v1_5/`.
- **ALINA** (Advanced Line Identification and Notation Algorithm) [3], applied to 60,249 taxiway frames of v1. Its limits on runway imagery are reported in [4].
- **HILL** (Human-In-the-Loop Labeling), introduced with v2 [2]: polylines and derived masks for Round 1 and Round 2 frames.

The ALINA and HILL annotations and the v3 reference split (train, validation and test manifests drawn by 15-second clips) are archived on Zenodo ([10.5281/zenodo.24448734](https://doi.org/10.5281/zenodo.24448734)). The record's metadata are public; its files are available on request until their public release.

## Download

| Record | Content | DOI |
|---|---|---|
| v1.1 (2023) | Repository snapshot of the original release: extracted frames and CDLEM labels | [10.5281/zenodo.8144439](https://doi.org/10.5281/zenodo.8144439) |
| Videos, all versions | Concept record: always resolves to the latest version | [10.5281/zenodo.24410169](https://doi.org/10.5281/zenodo.24410169) |
| Videos v1 | Original round, 15 videos | [10.5281/zenodo.24410170](https://doi.org/10.5281/zenodo.24410170) |
| Videos v2 | Round 1 (21 videos) and Round 2 (3 videos) | [10.5281/zenodo.24411351](https://doi.org/10.5281/zenodo.24411351) |
| Videos v3 | Complete set: original round and Rounds 1 to 3 (62 videos) | [10.5281/zenodo.24422418](https://doi.org/10.5281/zenodo.24422418) |
| Annotations and split v3 | CDLEM, ALINA and HILL labels, v3 reference split and `make_split.py` (files on request) | [10.5281/zenodo.24448734](https://doi.org/10.5281/zenodo.24448734) |

Versions v1 and v2 hold only the rounds they add; version v3 holds every video of release v3. Files are one uncompressed zip per camera folder; unzipping at the repository root places every video at its `path` in `metadata/manifest_v3.csv`.

## Publications

1. P. Ganeriwala, S. Bhattacharyya, S. Gunther, B. Kish, M. A. H. Khan and A. Dhadoti, "AssistTaxi: A Comprehensive Dataset for Taxiway Analysis and Autonomous Operations," *2023 International Conference on Machine Learning and Applications (ICMLA)*, IEEE, 2023. [doi:10.1109/ICMLA58977.2023.00163](https://doi.org/10.1109/ICMLA58977.2023.00163) · [arXiv:2409.06856](https://arxiv.org/abs/2409.06856)
2. P. Ganeriwala, M. A. H. Khan, A. Alvarez, S. Bhattacharyya, N. A. Neogi and S. Lehman, "AssistTaxi-v2: A Scalable Dataset for Taxiway/Runway Scene Understanding Under Diverse Conditions," *AIAA SCITECH 2026 Forum*, AIAA, 2026. [doi:10.2514/6.2026-1774](https://doi.org/10.2514/6.2026-1774)
3. M. A. H. Khan, P. Ganeriwala, S. Bhattacharyya, N. Neogi and R. Muthalagu, "ALINA: Advanced Line Identification and Notation Algorithm," *2024 IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops (CVPRW)*, IEEE, 2024. [doi:10.1109/CVPRW63382.2024.00725](https://doi.org/10.1109/CVPRW63382.2024.00725) · [arXiv:2406.08775](https://arxiv.org/abs/2406.08775)
4. P. Ganeriwala, A. Alvarez, A. AlQahtani, S. Bhattacharyya, M. A. H. Khan and N. Neogi, "Runway vs. Taxiway: Challenges in Automated Line Identification and Notation Approaches," *2025 IEEE International Systems Conference (SysCon)*, IEEE, 2025. [doi:10.1109/SysCon64521.2025.11014782](https://doi.org/10.1109/SysCon64521.2025.11014782) · [arXiv:2501.18494](https://arxiv.org/abs/2501.18494)

## Citation

If you use AssistTaxi, please cite the dataset papers [1] and [2] and the Zenodo record of the version you used; `CITATION.cff` has the same information in machine-readable form.

```bibtex
@inproceedings{ganeriwala2023assisttaxi,
  author    = {Ganeriwala, Parth and Bhattacharyya, Siddhartha and Gunther, Sean and Kish, Brian and Khan, Mohammed Abdul Hafeez and Dhadoti, Ankur},
  title     = {{AssistTaxi}: A Comprehensive Dataset for Taxiway Analysis and Autonomous Operations},
  booktitle = {2023 International Conference on Machine Learning and Applications (ICMLA)},
  publisher = {IEEE},
  year      = {2023},
  doi       = {10.1109/ICMLA58977.2023.00163}
}

@inproceedings{ganeriwala2026assisttaxi,
  author    = {Ganeriwala, Parth and Khan, Mohammad Abdul Hafeez and Alvarez, Amy and Bhattacharyya, Siddhartha and Neogi, Natasha A. and Lehman, Sarah},
  title     = {{AssistTaxi-v2}: A Scalable Dataset for Taxiway/Runway Scene Understanding Under Diverse Conditions},
  booktitle = {AIAA SCITECH 2026 Forum},
  publisher = {American Institute of Aeronautics and Astronautics},
  year      = {2026},
  doi       = {10.2514/6.2026-1774}
}

@misc{ganeriwala2023assisttaxizenodo,
  author    = {Ganeriwala, Parth and Bhattacharyya, Siddhartha and Gunther, Sean and Kish, Brian and Khan, Mohammed Abdul Hafeez and Dhadoti, Ankur and Neogi, Natasha},
  title     = {{AssistTaxi}: v1.1},
  publisher = {Zenodo},
  year      = {2023},
  doi       = {10.5281/zenodo.8144439}
}
```

## License

Apache License 2.0; see `LICENSE`.
