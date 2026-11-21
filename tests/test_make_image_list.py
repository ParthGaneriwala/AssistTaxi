import csv
import os
import tempfile
import unittest

from tools.make_image_list import make_image_list


class MakeImageListTest(unittest.TestCase):
    def test_filters_and_formats_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            metadata_dir = os.path.join(temp_dir, "metadata")
            os.makedirs(metadata_dir)

            with open(os.path.join(metadata_dir, "manifest_v3.csv"), "w",
                      newline="", encoding="utf-8") as manifest:
                writer = csv.writer(manifest)
                writer.writerow(["video_id", "release", "airport", "viewpoint"])
                writer.writerow(["r1-center-test", "v2", "KMLB", "center"])
                writer.writerow(["r3-center-other", "v3", "X26", "center"])

            with open(os.path.join(metadata_dir, "samples_v3.csv"), "w",
                      newline="", encoding="utf-8") as samples:
                writer = csv.writer(samples)
                writer.writerow(["video_id", "first_frame", "last_frame", "surface"])
                writer.writerow(["r1-center-test", "1", "2", "taxiway"])
                writer.writerow(["r1-center-test", "3", "3", "runway"])
                writer.writerow(["r3-center-other", "0", "1", "taxiway"])

            output = os.path.join(temp_dir, "images.txt")
            count = make_image_list(
                output,
                images_root="/data/assisttaxi",
                release="v2",
                airport="KMLB",
                viewpoint="center",
                surface="taxiway",
                metadata_dir=metadata_dir,
            )

            with open(output, encoding="utf-8") as image_list:
                lines = image_list.read().splitlines()

            self.assertEqual(count, 2)
            self.assertEqual(lines, [
                "/data/assisttaxi/r1-center-test-000001.jpg",
                "/data/assisttaxi/r1-center-test-000002.jpg",
            ])


if __name__ == "__main__":
    unittest.main()
