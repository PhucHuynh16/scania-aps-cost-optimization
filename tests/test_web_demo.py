"""Exercise the local dashboard against the saved experiment evidence."""

import json
from http import HTTPStatus
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import urlopen

from app import Handler, ThreadingHTTPServer, load_dashboard
from scripts import demo


class TestWebDemo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_dashboard()

    def test_integrity(self):
        self.assertEqual([group["checked"] for group in self.data["integrity"]], [11, 12, 9])
        self.assertTrue(all(group["status"] == "PASS" for group in self.data["integrity"]))

    def test_trial_history_matches_saved_study(self):
        data = self.data
        study = json.loads(demo.PHASE2_STUDY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(len(data["trials"]), 20)
        best_so_far = float("inf")
        for index, (trial, saved) in enumerate(zip(data["trials"], study["trials"])):
            with self.subTest(trial=index):
                self.assertEqual(trial["trial_number"], index)
                self.assertEqual(trial["objective_value"], saved["objective_value"])
                self.assertEqual(trial["threshold"], saved["best_policy"]["threshold"])
                best_so_far = min(best_so_far, saved["objective_value"])
                self.assertEqual(trial["best_so_far"], best_so_far)

    def test_results(self):
        self.assertEqual(self.data["selected"]["selected_trial"], 16)
        self.assertEqual(self.data["validation"]["total_cost"], 6330)
        self.assertEqual(self.data["test"]["total_cost"], 13840)
        test = self.data["test"]
        self.assertEqual([test[key] for key in ("TN", "FP", "FN", "TP")], [15141, 484, 18, 357])

    def test_default_rf_baselines_on_validation(self):
        rows = [row for row in self.data["baselines"] if "policy_id" in row]
        self.assertEqual([row["total_cost"] for row in rows], [28190, 5420])
        self.assertEqual([row["threshold"] for row in rows], [0.5, 0.1])
        self.assertEqual([row["M"] for row in rows], [163, 436])
        self.assertEqual([row["K"] for row in rows], [1200, 1200])
        self.assertEqual(self.data["validation"]["total_cost"] - rows[1]["total_cost"], 910)

    def test_every_validation_threshold_matches_the_saved_grid(self):
        grid = self.data["thresholds"]
        policy = json.loads(demo.PHASE2_BEST_POLICY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(len(grid), 101)
        for index, (point, saved) in enumerate(zip(grid, policy["threshold_curve"])):
            with self.subTest(index=index):
                self.assertEqual({key: point[key] for key in saved}, saved)
                self.assertEqual(sum(point[key] for key in ("TP", "FP", "FN", "TN")), policy["N"])
                self.assertEqual(point["cost"], 10 * point["FP"] + 500 * point["FN"])
                self.assertEqual(bool(point["feasible"]), point["M"] <= policy["K"])
        self.assertFalse(grid[4]["feasible"])
        self.assertTrue(grid[5]["feasible"])
        self.assertEqual(grid[32]["cost"], 6350)
        self.assertNotEqual(grid[32]["threshold"], self.data["validation"]["threshold"])

    def test_invalid_trial_record_is_rejected(self):
        load_json = demo.load_json_artifact

        def stale_record(path, description):
            record = load_json(path, description)
            if path.name == "trial_000_result.json":
                record["fit_index"] = 99
            return record

        with patch.object(demo, "load_json_artifact", side_effect=stale_record):
            with self.assertRaisesRegex(demo.DemoIntegrityError, "Trial 0"):
                load_dashboard()


class TestWebDemoHTTP(unittest.TestCase):
    def test_assets_api_and_error_response(self):
        with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base = f"http://127.0.0.1:{server.server_port}"
                for path, content_type in {
                    "/": "text/html",
                    "/style.css": "text/css",
                    "/dashboard.js": "text/javascript",
                    "/figures/convergence.png": "image/png",
                    "/figures/tradeoff.png": "image/png",
                }.items():
                    with self.subTest(path=path), urlopen(base + path, timeout=5) as response:
                        self.assertEqual(response.status, HTTPStatus.OK)
                        self.assertEqual(response.headers.get_content_type(), content_type)
                        self.assertTrue(response.read())
                with urlopen(base + "/api/evidence", timeout=5) as response:
                    self.assertEqual(json.load(response)["test"]["total_cost"], 13840)
                with patch("app.load_dashboard", side_effect=demo.DemoIntegrityError("Sai mã băm")):
                    with self.assertRaises(HTTPError) as failed:
                        urlopen(base + "/api/evidence", timeout=5)
                    with failed.exception as response:
                        self.assertEqual(response.code, HTTPStatus.INTERNAL_SERVER_ERROR)
                        self.assertEqual(json.load(response), {"error": "Sai mã băm"})
            finally:
                server.shutdown()
                thread.join()


if __name__ == "__main__":
    unittest.main()
