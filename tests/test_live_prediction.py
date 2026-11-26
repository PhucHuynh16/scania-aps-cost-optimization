import csv
from http.client import HTTPConnection
import io
import json
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory
from threading import Thread
import unittest

import joblib
import numpy as np

from app import Handler, ThreadingHTTPServer
from src.scania.contracts import FEATURES
from src.scania.live_prediction import (
    CHECKPOINT_DIR, CheckpointError, MAX_ROWS, MAX_UPLOAD_BYTES, PREPROCESSOR,
    UploadError, parse_csv, predict_csv, read_release,
)


ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "data/examples/scania_validation_sample.csv"


def encode(rows):
    string = io.StringIO()
    csv.writer(string).writerows(rows)
    return string.getvalue().encode("utf-8")


class LivePredictionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample = SAMPLE.read_bytes()
        cls.rows = list(csv.reader(cls.sample.decode().splitlines()))

    def test_prediction_matches_checkpoint_and_g3(self):
        raw_rows, labels = parse_csv(self.sample, FEATURES)
        provenance = json.loads((SAMPLE.parent / "sample_provenance.json").read_text(encoding="utf-8"))
        X = np.load(ROOT / PREPROCESSOR.replace("tree_preprocessor.joblib", "tree_validation.npy"), mmap_mode="r")
        model = joblib.load(ROOT / CHECKPOINT_DIR / "random_forest.joblib")
        preprocessor = joblib.load(ROOT / PREPROCESSOR)
        transformed = preprocessor.transform(np.asarray(raw_rows))
        self.assertTrue(np.isnan(raw_rows).any())
        np.testing.assert_array_equal(transformed, X[provenance["validation_positions_zero_based"]])
        result = predict_csv(self.sample)
        np.testing.assert_array_equal(result["scores"], model.predict_proba(transformed)[:, 1])
        self.assertEqual(result["labels"], labels)
        self.assertEqual(result["threshold"], 0.3232440937634324)

    def test_unlabeled_rows_keep_same_scores(self):
        result = predict_csv(encode([row[1:] for row in self.rows]))
        self.assertIsNone(result["labels"])
        self.assertEqual(result["scores"], predict_csv(self.sample)["scores"])

    def test_invalid_input(self):
        cases = {
            "missing": encode([row[:-1] for row in self.rows]),
            "duplicate": encode([self.rows[0][:-1] + [self.rows[0][1]], self.rows[1]]),
            "wrong order": encode([row[:1] + row[2:3] + row[1:2] + row[3:] for row in self.rows]),
            "nonfinite": encode([self.rows[0], self.rows[1][:1] + ["1e1000"] + self.rows[1][2:]]),
            "wrong type": encode([self.rows[0], self.rows[1][:1] + ["truck"] + self.rows[1][2:]]),
            "bad label": encode([self.rows[0], ["other"] + self.rows[1][1:]]),
            "width": encode([self.rows[0], self.rows[1][:-1]]),
            "empty": b"",
            "header only": encode([self.rows[0]]),
            "too many bytes": b" " * (MAX_UPLOAD_BYTES + 1),
            "too many rows": encode([self.rows[0]] + [self.rows[1]] * (MAX_ROWS + 1)),
        }
        for name, payload in cases.items():
            with self.subTest(name=name), self.assertRaises(UploadError):
                parse_csv(payload, FEATURES)

    def test_checkpoint_missing_or_modified(self):
        names = ["configs/scania/live_model.json", *(
            f"{CHECKPOINT_DIR}/{name}" for name in ("manifest.json", "model_metadata.json", "feature_schema.json")
        )]
        with TemporaryDirectory() as directory:
            home = Path(directory)
            for name in names:
                dest = home / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                copyfile(ROOT / name, dest)
            with self.assertRaisesRegex(CheckpointError, "Thiếu"):
                read_release(home)
            (home / CHECKPOINT_DIR / "random_forest.joblib").write_bytes(b"broken")
            with self.assertRaisesRegex(CheckpointError, "SHA-256"):
                read_release(home)

    def test_http_post_sample_and_limits(self):
        with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                headers = {"Content-Type": "text/csv"}
                for expected, payload, request_headers in (
                    (200, self.sample, headers),
                    (400, b"", headers),
                    (400, b"wrong\nnot-a-row\n", headers),
                    (413, b"", {**headers, "Content-Length": str(MAX_UPLOAD_BYTES + 1)}),
                    (415, b"", {"Content-Type": "application/octet-stream"}),
                ):
                    with self.subTest(status=expected):
                        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
                        try:
                            connection.request("POST", "/api/predict", payload, request_headers)
                            response = connection.getresponse()
                            self.assertEqual(response.status, expected)
                            data = json.loads(response.read())
                            if expected == 200:
                                self.assertEqual(len(data["scores"]), 12)
                            else:
                                self.assertIn("error", data)
                        finally:
                            connection.close()
            finally:
                server.shutdown()
                thread.join()


if __name__ == "__main__":
    unittest.main()
