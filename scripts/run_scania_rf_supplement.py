"""Owner-approved, once-only RF supplement on G3 Train and Validation."""

import argparse
import csv
from hashlib import file_digest, sha256
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from uuid import uuid4

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "configs/scania/rf_supplement.json"
OUT = ROOT / "results/scania_aps/rf_supplement"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, record):
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, indent=2, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def digest(path):
    with path.open("rb") as handle:
        return file_digest(handle, "sha256").hexdigest()


def environment():
    lock = ROOT / "configs/scania/phase2_requirements.lock.txt"
    expected = dict(line.split("==") for line in lock.read_text().splitlines() if "==" in line)
    actual = {name: version(name) for name in expected}
    if platform.python_version() != "3.11.9" or expected != actual:
        raise ValueError("Use Python 3.11.9 and the Phase 2 lockfile.")
    return {"python": platform.python_version(), "packages": actual, "platform": platform.platform()}


def frozen_policy(evidence):
    trial = evidence["p2_trial_best"]
    source = evidence["g10_policy"]["source_policy"]
    fixed = evidence["phase2_cfg"]["estimator_fixed_params"]
    params = {**fixed, **trial["rf_params"]}
    threshold = evidence["p2_best"]["threshold"]
    if (
        params != source["hyperparameters"]
        or params != evidence["g10_cfg"]["source_policy"]["rf_hyperparameters"]
        or trial["trial_number"] != 16
        or source["selected_trial"] != 16
        or threshold != source["frozen_threshold"]
    ):
        raise ValueError("The historical Phase 2 and frozen G10 policy records disagree.")
    return params, threshold


def preflight(config):
    from scripts import demo
    from src.scania.g4_b1_windows import memory_snapshot
    from src.scania.g4_b2_executor import verify_g3_artifacts_and_build_allowlist

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != config["source_head"]:
        raise ValueError(f"Unexpected source HEAD: {head}")
    if not demo.verify_all_artifact_checksums(verbose=False):
        raise ValueError("Historical artifact verification failed.")
    frozen_policy(demo.load_and_validate_all_evidence())
    g3 = config["g3_run"]
    g3_manifest = ROOT / "results/scania_aps/g3" / g3 / "stable_manifest.json"
    if sha256(g3_manifest.read_bytes().replace(b"\r\n", b"\n")).hexdigest() != config["g3_manifest_sha256"]:
        raise ValueError("G3 manifest SHA-256 mismatch.")
    _, data = verify_g3_artifacts_and_build_allowlist(ROOT, g3)
    archive = ROOT / "data/processed/scania_aps" / g3
    preprocessor = archive / "tree_preprocessor.joblib"
    if digest(preprocessor) != config["preprocessor_sha256"]:
        raise ValueError("G3 tree preprocessor SHA-256 mismatch.")
    data["binary_sha256"] = {
        name: digest(archive / name)
        for name in ("tree_train.npy", "tree_validation.npy", "membership.npz", preprocessor.name)
    }
    resources = memory_snapshot()
    if resources["available_commit_bytes"] < config["max_ram_mib"] * 1024**2:
        raise ValueError("Insufficient available memory commit for the job limit.")
    return environment(), data, resources


def score(y, p, threshold):
    import numpy as np
    from sklearn.metrics import average_precision_score, roc_auc_score
    from src.scania.cost_model import observed_aps_cost
    from src.scania.constraints import capacity_report

    decisions = (p >= threshold).astype(np.int8)
    result = observed_aps_cost(y, decisions)
    result.update(capacity_report(decisions))
    tp, m, positives = (result[key] for key in ("TP", "M", "P"))
    result.update(
        threshold=threshold,
        precision=tp / m if m else None,
        recall=tp / positives if positives else None,
        f1=2 * tp / (m + positives) if m + positives else None,
        roc_auc=float(roc_auc_score(y, p)),
        average_precision=float(average_precision_score(y, p)),
    )
    return result


def write_metrics(output, rows):
    with (output / "metrics.csv").open("x", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["policy", *next(iter(rows.values()))])
        writer.writeheader()
        for policy, metrics in rows.items():
            writer.writerow({"policy": policy, **metrics})


def worker(kind, reservation, config):
    from src.scania.g4_env_discovery import NativeSession, THREAD_ENV, prepare_imports

    prepare_imports()
    import joblib
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    from scripts import demo
    from src.scania.contracts import FEATURES
    from src.scania.g4_b2_executor import install_executor_io_guard
    from src.scania.phase2_optimization import evaluate_threshold_candidates_vectorized

    output = OUT / config["runs"][kind]["run_id"]
    task = read(output / "run_config.json")
    if (
        reservation != task["reservation"]
        or os.environ.get("SCANIA_RF_RESERVATION") != reservation
        or task["approval_sha256"] != config["authorization"]["document_sha256"]
        or task["config_sha256"] != digest(CONFIG)
        or any(os.environ.get(key) != value for key, value in THREAD_ENV.items())
    ):
        raise ValueError("This worker requires the authorized, isolated supervisor.")
    environment()
    evidence = demo.load_and_validate_all_evidence()
    official_params, tau = frozen_policy(evidence)
    params = config["runs"]["default"]["params"] if kind == "default" else official_params
    if kind == "default" and params != {"random_state": 42, "n_jobs": 1}:
        raise ValueError("Default RF permits only seed and thread controls.")

    data_dir = ROOT / "data/processed/scania_aps" / config["g3_run"]
    names = ("tree_train.npy", "tree_validation.npy", "membership.npz")
    paths = [data_dir / name for name in names]
    install_executor_io_guard(ROOT, output, paths)
    for name, path in zip(names, paths):
        if digest(path) != task["data"]["binary_sha256"][name]:
            raise ValueError(f"Data changed after preflight: {name}")
    x_train, x_val = [np.load(path, allow_pickle=False, mmap_mode="r") for path in paths[:2]]
    with np.load(paths[2], allow_pickle=False) as labels:
        y_train, y_val = labels["y_train"], labels["y_validation"]
    model = RandomForestClassifier(**params)
    with NativeSession() as session:
        pools = session.controller.info()
        if not pools or any(pool["num_threads"] != 1 for pool in pools):
            raise ValueError("Native thread control was not verified.")
        start = time.perf_counter()
        write(output / "fit_started.json", {"fit": 1, "parameters": model.get_params()})
        try:
            model.fit(x_train, y_train)
        except Exception as exc:
            write(output / "fit_failed.json", {"error": str(exc), "fit_seconds": time.perf_counter() - start})
            raise
        fit_time = time.perf_counter() - start
        write(output / "fit_completed.json", {"fit": 1, "fit_seconds": fit_time})
        if list(model.classes_) != [0, 1]:
            raise ValueError("Unexpected class order.")
        start = time.perf_counter()
        probability = model.predict_proba(x_val)[:, 1]
        predict_time = time.perf_counter() - start
    selection = evaluate_threshold_candidates_vectorized(y_val, probability)
    verification = None
    if kind == "default":
        rows = {"default_0_5": score(y_val, probability, 0.5)}
        if selection["best"] is None:
            raise ValueError("No feasible default RF threshold found.")
        rows["default_optimized_threshold"] = score(y_val, probability, selection["best"]["threshold"])
    else:
        rows = {"trial16_frozen": score(y_val, probability, tau)}
        metrics = rows["trial16_frozen"]
        historical = evidence["p2_trial_best"]
        keys = ("TP", "FP", "FN", "TN", "total_cost", "M", "K")
        verification = {
            "frozen_metrics_match": all(metrics[key] == evidence["p2_best"][key] for key in keys),
            "validation_guard_match": all(metrics[key] == evidence["g10_val_guard"][key] for key in keys),
            "roc_auc_match": abs(metrics["roc_auc"] - historical["roc_auc"]) <= 1e-12,
            "average_precision_match": abs(metrics["average_precision"] - historical["pr_auc"]) <= 1e-12,
            "threshold_curve_match": selection.get("threshold_curve") == evidence["p2_best"]["threshold_curve"],
            "selected_threshold_match": (selection.get("best") or {}).get("threshold") == tau,
            "historical_row_scores_available": False,
        }
        passed = all(value for key, value in verification.items() if key != "historical_row_scores_available")
        verification["status"] = "PASS" if passed else "MISMATCH"
        if passed:
            joblib.dump(model, output / "random_forest.joblib", compress=3)
            write(output / "feature_schema.json", {"features": FEATURES, "missing": ["na", ""], "target": "class"})
    write_metrics(output, rows)
    write(output / "metrics.json", {
        "policies": rows, "parameters": model.get_params(), "validation_only": True,
        "selected_candidate_count": selection["candidate_count"],
        "fit_seconds": fit_time, "predict_seconds": predict_time,
        "native_pools": [{"internal_api": p["internal_api"], "threads": p["num_threads"]} for p in pools],
        "verification": verification,
    })
    if verification and verification["status"] != "PASS":
        raise ValueError("Checkpoint differs from Trial 16. Review metrics.json before integration.")


def run(kind, config, approval):
    from src.scania.g4_b1_windows import WindowsJob
    from src.scania.g4_env_discovery import THREAD_ENV

    if not approval or digest(approval) != config["authorization"]["document_sha256"]:
        raise ValueError("Provide the exact owner directive as --approval-file.")
    if config["total_max_fits"] != 2 or any(run["max_fits"] != 1 for run in config["runs"].values()):
        raise ValueError("Invalid owner fit budget.")
    env, data, resources = preflight(config)
    run_cfg = config["runs"][kind]
    output = OUT / run_cfg["run_id"]
    prior_fits = [p for p in OUT.glob("*/fit_started.json")]
    if len(prior_fits) >= config["total_max_fits"] or any(
        read(path.parent / "run_config.json")["kind"] == kind for path in prior_fits
    ):
        raise ValueError(f"Fit budget already consumed for {kind}.")
    output.mkdir(parents=True, exist_ok=False)
    token = uuid4().hex
    write(output / "run_config.json", {
        "run_id": run_cfg["run_id"], "kind": kind, "source_head": config["source_head"],
        "config_sha256": digest(CONFIG), "runner_sha256": digest(Path(__file__)),
        "approval_sha256": config["authorization"]["document_sha256"],
        "data": data, "environment": env, "host_before": resources, "reservation": token,
        "resource_limits": {"max_ram_mib": config["max_ram_mib"], "max_native_threads": 1,
                            "max_wall_seconds": run_cfg["max_wall_seconds"]},
    })
    child_env = dict(os.environ, **THREAD_ENV, SCANIA_RF_RESERVATION=token)
    job = WindowsJob([sys.executable, "-B", "-X", "utf8", "-m", "scripts.run_scania_rf_supplement",
                      "worker", kind, "--reservation", token],
                     child_env, ROOT, config["max_ram_mib"] * 1024**2)
    start = time.perf_counter()
    try:
        job.resume()
        exit_code = job.poll()
        while exit_code is None and time.perf_counter() - start < run_cfg["max_wall_seconds"]:
            time.sleep(0.1)
            exit_code = job.poll()
        if exit_code is None:
            job.terminate()
            job.wait_empty(5)
        peak = job.limits()["peak_job_memory_bytes"]
    finally:
        job.close()
    write(output / "run_summary.json", {
        "run_id": run_cfg["run_id"], "status": "COMPLETE" if exit_code == 0 else "FAILED",
        "fit_used": int((output / "fit_started.json").exists()),
        "wall_seconds": time.perf_counter() - start, "peak_job_memory_bytes": peak,
        "worker_exit": exit_code,
    })
    if kind == "checkpoint" and exit_code == 0:
        metrics = read(output / "metrics.json")
        write(output / "model_metadata.json", {
            "model_version": run_cfg["run_id"], "source_trial": 16,
            "purpose": "Supplemental refit for live inference", "package_versions": env,
            "parameters": metrics["parameters"], "threshold": metrics["policies"]["trial16_frozen"]["threshold"],
            "preprocessor": {"path": f"data/processed/scania_aps/{config['g3_run']}/tree_preprocessor.joblib",
                             "sha256": config["preprocessor_sha256"]},
            "training_fingerprint": data,
            "validation_verification": metrics["verification"],
        })
    write(output / "manifest.json", {path.name: digest(path) for path in sorted(output.iterdir()) if path.is_file()})
    print(json.dumps(read(output / "run_summary.json")), flush=True)
    if exit_code != 0:
        failure = output / "worker_error.json"
        raise ValueError(f"Worker failed: {read(failure) if failure.exists() else exit_code}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("preflight", "execute", "worker"))
    parser.add_argument("kind", choices=("default", "checkpoint"), nargs="?")
    parser.add_argument("--approval-file", type=Path)
    parser.add_argument("--reservation")
    args = parser.parse_args()
    config = read(CONFIG)
    if args.command == "preflight":
        env, data, resources = preflight(config)
        print(json.dumps({"python": env["python"], "data": data, "host": resources}, indent=2))
    elif not args.kind:
        parser.error("Select default or checkpoint.")
    elif args.command == "execute":
        run(args.kind, config, args.approval_file)
    else:
        try:
            worker(args.kind, args.reservation, config)
        except Exception as exc:
            output = OUT / config["runs"][args.kind]["run_id"]
            if output.is_dir() and args.reservation == os.environ.get("SCANIA_RF_RESERVATION"):
                write(output / "worker_error.json", {"type": type(exc).__name__, "error": str(exc)})
            raise


if __name__ == "__main__":
    main()
