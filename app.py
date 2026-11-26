"""Serve the saved Scania APS experiment results on the local machine."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import BoundedSemaphore
from urllib.parse import urlsplit

from scripts import demo
from src.scania.live_prediction import CheckpointError, MAX_UPLOAD_BYTES, UploadError, predict_csv


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "web_demo"
INFERENCE_SLOT = BoundedSemaphore(1)
TRIALS_PATH = demo.PHASE2_RUN_DIR / "trials_summary.csv"
DEFAULT_RF_DIR = ROOT / "results/scania_aps/rf_supplement/default_rf_20261127_02"
DEFAULT_RF_METRICS = DEFAULT_RF_DIR / "metrics.json"

ASSET_ROUTES = {
    "/": (ASSETS / "index.html", "text/html; charset=utf-8"),
    "/style.css": (ASSETS / "style.css", "text/css; charset=utf-8"),
    "/dashboard.js": (ASSETS / "dashboard.js", "text/javascript; charset=utf-8"),
    "/live.js": (ASSETS / "live.js", "text/javascript; charset=utf-8"),
    "/validation-sample.csv": (ROOT / "data/examples/scania_validation_sample.csv",
                               "text/csv; charset=utf-8"),
    "/figures/convergence.png": (demo.FIG_CONVERGENCE, "image/png"),
    "/figures/tradeoff.png": (demo.FIG_TRADEOFF, "image/png"),
}


def load_trials(evidence):
    config = evidence["phase2_cfg"]
    study = evidence["p2_study"]
    rows = demo.load_csv_artifact(TRIALS_PATH, "Lịch sử Optuna TPE")
    if len(rows) != len(study["trials"]) or len(rows) != config["budget"]["max_trials"]:
        raise demo.DemoIntegrityError("Số trial trong CSV, study và cấu hình không khớp.")

    trials = []
    best_cost = float("inf")
    for index, (row, trial) in enumerate(zip(rows, study["trials"])):
        policy = trial["best_policy"]
        demo.validate_policy_metrics(
            policy, evidence["cost_fp_unit"], evidence["cost_fn_unit"], f"Trial {index}"
        )
        durable = demo.load_json_artifact(
            demo.PHASE2_RUN_DIR / f"durable_fits/trial_{index:03}_result.json",
            f"Kết quả lưu riêng của Trial {index}",
        )
        if trial != durable or trial["trial_number"] != index or trial["fit_index"] != index + 1:
            raise demo.DemoIntegrityError(f"Hồ sơ JSON của Trial {index} không khớp.")
        if row["status"] != trial["status"] or trial["status"] != policy["policy_status"]:
            raise demo.DemoIntegrityError(f"Trạng thái của Trial {index} không khớp.")
        if trial["objective_value"] != policy["total_cost"] or not policy["feasible"]:
            raise demo.DemoIntegrityError(f"Chi phí hoặc tính khả thi của Trial {index} không khớp.")
        if any(policy[k] != evidence["p2_best"][k] for k in ("N", "P", "K")):
            raise demo.DemoIntegrityError(f"Phân vùng Validation của Trial {index} không khớp.")

        items = {
            "trial_number": index,
            "fit_index": trial["fit_index"],
            "objective_value": trial["objective_value"],
            "fit_seconds": trial["fit_seconds"],
            "predict_seconds": trial["predict_seconds"],
            **trial["rf_params"],
            **{key: policy[key] for key in ("threshold", "TP", "FP", "FN", "TN", "M", "saving_pct")},
        }
        if any(float(row[key]) != value for key, value in items.items()):
            raise demo.DemoIntegrityError(f"CSV và JSON không khớp ở Trial {index}.")
        best_cost = min(best_cost, items["objective_value"])
        items["best_so_far"] = best_cost
        trials.append(items)
    return trials


def load_thresholds(best, saved_trial):
    if best != saved_trial["best_policy"]:
        raise demo.DemoIntegrityError("Đường cong ngưỡng và chính sách của trial được chọn không khớp.")

    # The archive stores TP/FP/FN at each grid point. TN is the remaining
    # negative count of the same Validation partition.
    thresholds = []
    negatives = best["N"] - best["P"]
    for index, point in enumerate(best["threshold_curve"]):
        tp, fp, fn = (point[key] for key in ("TP", "FP", "FN"))
        if (
            point["threshold"] != index / 100
            or tp + fn != best["P"]
            or min(tp, fp, fn) < 0
            or fp > negatives
        ):
            raise demo.DemoIntegrityError(f"Điểm ngưỡng Validation {index}/100 không hợp lệ.")
        thresholds.append({**point, "TN": negatives - fp})
    return thresholds


def load_default_rf_baselines(evidence):
    manifest = demo.load_json_artifact(DEFAULT_RF_DIR / "manifest.json", "Manifest RF mặc định")
    payload = DEFAULT_RF_METRICS.read_bytes()
    if sha256(payload).hexdigest() != manifest["metrics.json"]:
        raise demo.DemoIntegrityError("SHA-256 sai lệch ở kết quả RF mặc định.")
    metrics = json.loads(payload)
    params = metrics["parameters"]
    if not metrics["validation_only"] or params["class_weight"] is not None:
        raise demo.DemoIntegrityError("Phạm vi hoặc trọng số lớp của RF mặc định sai lệch.")
    rows = []
    for key, label in (
        ("default_0_5", "RF mặc định"),
        ("default_optimized_threshold", "RF mặc định + quét ngưỡng"),
    ):
        row = metrics["policies"][key]
        demo.validate_policy_metrics(row, evidence["cost_fp_unit"], evidence["cost_fn_unit"], label)
        if any(row[field] != evidence["p2_best"][field] for field in ("N", "P", "K")):
            raise demo.DemoIntegrityError(f"Phân vùng Validation của {label} không khớp.")
        rows.append({**row, "baseline_id": label, "policy_id": key})
    return rows


def load_dashboard():
    evidence = demo.load_and_validate_all_evidence()
    groups = (
        (demo.G4_RUN_DIR, demo.G4_CHECKSUMS_PATH, 11),
        (demo.PHASE2_RUN_DIR, demo.PHASE2_CHECKSUMS_PATH, 12),
        (demo.G10_RUN_DIR, demo.G10_MANIFEST_PATH, 9),
    )
    integrity = []
    for directory, manifest, expected in groups:
        ok, records = demo.verify_manifest_group(directory, manifest, directory.name)
        if not ok or len(records) != expected:
            raise demo.DemoIntegrityError(f"Kiểm tra SHA-256 thất bại ở {directory.name}.")
        integrity.append({"run": directory.name, "checked": len(records), "status": "PASS"})

    best = evidence["p2_best"]
    selected = evidence["g10_policy"]["source_policy"]
    saved_trial = evidence["p2_trial_best"]
    if selected["selected_trial"] != saved_trial["trial_number"] or selected["frozen_threshold"] != best["threshold"]:
        raise demo.DemoIntegrityError("Mã trial hoặc ngưỡng đóng băng không khớp.")

    return {
        "validation": {key: value for key, value in best.items() if key != "threshold_curve"},
        "test": evidence["g10_test"],
        "thresholds": load_thresholds(best, saved_trial),
        "trials": load_trials(evidence),
        "baselines": [*evidence["g4_rows"], *load_default_rf_baselines(evidence)],
        "config": evidence["phase2_cfg"],
        "selected": selected,
        "integrity": integrity,
        "source": {
            label: path.relative_to(ROOT).as_posix()
            for label, path in {
                "Baseline G4": demo.G4_METRICS_PATH,
                "Baseline RF mặc định": DEFAULT_RF_METRICS,
                "Optuna TPE": TRIALS_PATH,
                "Ngưỡng Validation": demo.PHASE2_BEST_POLICY_PATH,
                "Official Test": demo.G10_TEST_METRICS_PATH,
                "Ma trận Official Test": demo.G10_CM_CSV_PATH,
            }.items()
        },
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/evidence":
            self.send_evidence()
            return
        if path == "/favicon.ico":
            self.respond(HTTPStatus.NO_CONTENT, "image/x-icon", b"")
            return
        asset = ASSET_ROUTES.get(path)
        if asset is None:
            self.respond(HTTPStatus.NOT_FOUND, "text/plain; charset=utf-8", b"Not found")
            return
        file, content_type = asset
        try:
            body = file.read_bytes()
        except OSError:
            self.respond(HTTPStatus.NOT_FOUND, "text/plain; charset=utf-8", b"Missing asset")
            return
        self.respond(HTTPStatus.OK, content_type, body)

    def do_POST(self):
        self.close_connection = True
        if urlsplit(self.path).path != "/api/predict":
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "Không tìm thấy API."})
            return
        if self.headers.get_content_type() != "text/csv" or self.headers.get("Transfer-Encoding"):
            self.send_json(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, {"error": "Chỉ nhận nội dung text/csv."})
            return
        length = self.headers.get("Content-Length", "")
        if not length.isascii() or not length.isdigit() or len(length) > 10:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Kích thước tệp CSV không hợp lệ."})
            return
        count = int(length)
        if count > MAX_UPLOAD_BYTES:
            self.send_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "Tệp CSV vượt giới hạn 4 MiB."})
            return
        if not INFERENCE_SLOT.acquire(blocking=False):
            self.send_json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "Đang xử lý một lô khác. Vui lòng thử lại."})
            return
        try:
            self.connection.settimeout(10)
            payload = self.rfile.read(count)
            if len(payload) != count:
                raise UploadError("Tệp CSV tải lên chưa đầy đủ.")
            self.send_json(HTTPStatus.OK, predict_csv(payload))
        except UploadError as exc:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except CheckpointError as exc:
            self.send_json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": str(exc)})
        except TimeoutError:
            self.send_json(HTTPStatus.REQUEST_TIMEOUT, {"error": "Quá thời gian nhận CSV."})
        finally:
            INFERENCE_SLOT.release()

    def send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.respond(status, "application/json; charset=utf-8", body)

    def send_evidence(self):
        try:
            payload = json.dumps(load_dashboard(), ensure_ascii=False, allow_nan=False)
        except (demo.DemoIntegrityError, OSError, ValueError, KeyError, TypeError) as exc:
            payload = json.dumps({"error": str(exc)}, ensure_ascii=False)
            self.respond(HTTPStatus.INTERNAL_SERVER_ERROR, "application/json; charset=utf-8", payload.encode("utf-8"))
            return
        self.respond(HTTPStatus.OK, "application/json; charset=utf-8", payload.encode("utf-8"))

    def respond(self, status, content_type, body):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        if status != HTTPStatus.NO_CONTENT:
            self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        if body:
            self.wfile.write(body)


def main():
    from src.scania.g4_env_discovery import THREAD_ENV

    os.environ.update(THREAD_ENV)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8501)
    parser.add_argument("--verify", action="store_true", help="Verify artifacts and exit without starting the server")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    try:
        data = load_dashboard()
        checked = sum(group["checked"] for group in data["integrity"])
        print(f"PASS: {checked} artifacts; {len(data['trials'])} trials; {len(data['thresholds'])} Validation grid points.")
        if not args.verify:
            with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
                print(f"Web Demo: http://localhost:{server.server_port} (Ctrl+C để dừng)", flush=True)
                server.serve_forever()
    except KeyboardInterrupt:
        return 0
    except (demo.DemoIntegrityError, OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Web Demo: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
