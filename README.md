# AssistTaxi

AssistTaxi is a real-world dataset of taxiway and runway imagery for airport surface perception. It is collected at Melbourne Orlando International Airport (KMLB), Grant-Valkaria (X59) and, from v3, Sebastian Municipal (X26), from the cockpit of a Piper Cherokee Warrior and from a ground vehicle.

The dataset is released in versions. Each version adds collection rounds to the previous one and never removes or changes earlier samples, so **v3 = v1 + v2 + the v3 round**.

## Repository layout

```
v1/  original_daytime/            Original round, cockpit, daytime      (introduced in v1)
       camera-center/ camera-left/ camera-right/   videos  -> Zenodo
       video_stats.csv                             per-video stream statistics and airport
v2/  round1_glare/                Round 1, cockpit, early-morning glare (introduced in v2)
       camera-center/ camera-left/ camera-right/   videos  -> Zenodo
       video_stats.csv
     round2_vehicle_night/        Round 2, ground vehicle, night        (introduced in v2)
       camera-bottom/ camera-middle/ camera-top/   videos  -> Zenodo
       video_stats.csv
v3/  round3_dusk_night/           Round 3, cockpit, dusk to night       (introduced in v3)
       camera-center/                              videos  -> Zenodo (single camera)
       video_stats.csv
*/*/frame_examples/               one example frame per video, named by sample ID
metadata/                         release schema, video and sample manifests (see Metadata)
labels/cdlem/v1_5/                contour (CDLEM) polylines for video 5 of v1, as released in v1.1
tools/                            frame extraction, video statistics, manifest generation
docs/                             Round 2 vehicle: car_setup.jpg (camera mount), instances/ (views)
```

Only example frames are stored here. Videos (`*.MP4`) are published on Zenodo (see [Download](#download)); extracted frames are not distributed, and `tools/extract.py` reproduces them from the videos.

## Collection rounds

| Round | Date | Airports | Platform | Condition | Introduced in | Approx. frames |
|---|---|---|---|---|---|---|
| Original | May 19, 2022; Feb. 19, 2023 | KMLB, X59 | Cockpit | Daytime | v1 | 350,000 |
| Round 1 | Dec. 17, 2024 | KMLB, X59 | Cockpit | Early-morning glare | v2 | 650,000 |
| Round 2 | Apr. 23, 2025 | X59 | Vehicle | Night | v2 | 324,000 |
| Round 3 | Feb. 26, 2026 | KMLB, X59, X26 | Cockpit | Dusk to night | v3 | 530,000 |

Frame counts for Rounds 1 to 3 are estimates derived from recorded duration, at 60 frames per second for Rounds 1 and 2 and at each video's native frame rate for Round 3.

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

`python tools/validate.py` checks a release against the specification: unique identifiers, factor values in the schema with no unknowns on sampled videos, disjoint sample ranges within each video, and, where the reference split is present, disjoint blocks that contain only samples, guard intervals between blocks and one labeled camera per run. It also checks that the v1 contour labels are unchanged since the v1.1 tag.

## Extracting frames

```
python tools/extract.py <video.MP4> <out_dir> --video-id <video_id> [--samples metadata/samples_v3.csv]
```

writes `<video_id>-<frame index>.jpg`, matching the sample IDs; `--samples` keeps only frames that are samples. Without `--video-id`, the script keeps the 100 sharpest frames of the video.

## Annotations and reference split

Three labeling procedures have been applied to AssistTaxi imagery, and each is kept as its own modality:

- **CDLEM** (contour detection and line extraction), introduced with v1 [1]. The polylines for video 5 are in `labels/cdlem/v1_5/`.
- **ALINA** (Advanced Line Identification and Notation Algorithm) [3], applied to 60,249 taxiway frames of v1. Its limits on runway imagery are reported in [4].
- **HILL** (Human-In-the-Loop Labeling), introduced with v2 [2]: polylines and derived masks for Round 1 and Round 2 frames.

The ALINA and HILL annotations and the v3 reference split (train, validation and test manifests drawn by 15-second clips) will be published here and on Zenodo before the v3 release.

## Download

| Record | Content | DOI |
|---|---|---|
| v1.1 (2023) | Repository snapshot of the original release: extracted frames and CDLEM labels | [10.5281/zenodo.8144439](https://doi.org/10.5281/zenodo.8144439) |
| v1 videos | Original round, 15 videos | to be added |
| Round 1, center | 7 videos | to be added |
| Round 1, left and right | 14 videos | to be added |
| Round 2 | 3 videos | to be added |
| Round 3 | 23 videos | to be added |

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
