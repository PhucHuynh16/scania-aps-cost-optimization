"""Validate CSV uploads and score them with the verified internal checkpoint."""

import csv
from hashlib import sha256
from importlib.metadata import version
import io
import json
import math
from pathlib import Path
import platform
import re

ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT = "trial16_refit_20261127_02"
CHECKPOINT_DIR = f"results/scania_aps/rf_supplement/{CHECKPOINT}"
PREPROCESSOR = "data/processed/scania_aps/official_20261029_04/tree_preprocessor.joblib"
MAX_UPLOAD_BYTES = 4 * 1024 * 1024
MAX_ROWS = 1000
MAX_FLOAT32 = 3.4028234663852886e38
NUMBER = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", re.ASCII)


class UploadError(ValueError):
    """Invalid tabular input."""


class CheckpointError(RuntimeError):
    """Missing, inconsistent or incompatible internal files."""


def parse_csv(payload, features):
    if not payload:
        raise UploadError("Tệp CSV rỗng.")
    if len(payload) > MAX_UPLOAD_BYTES:
        raise UploadError("Tệp CSV vượt giới hạn 4 MiB.")
    try:
        reader = csv.reader(io.StringIO(payload.decode("utf-8-sig"), newline=""), strict=True)
        header = [field.strip() for field in next(reader, [])]
        if len(header) != len(set(header)):
            raise UploadError("Tên cột bị trùng.")
        actual = [field for field in header if field != "class"]
        missing = [field for field in features if field not in actual]
        unexpected = [field for field in actual if field not in features]
        if missing or unexpected:
            detail = []
            if missing:
                detail.append(f"thiếu {len(missing)} cột ({', '.join(missing[:3])})")
            if unexpected:
                detail.append(f"có {len(unexpected)} cột ngoài schema")
            raise UploadError("CSV không đúng schema Scania APS: " + ", ".join(detail) + ".")
        if actual != list(features):
            raise UploadError("170 thuộc tính phải theo đúng thứ tự trong CSV mẫu.")
        target = header.index("class") if "class" in header else None
        positions = [position for position in range(len(header)) if position != target]
        rows = []
        labels = [] if target is not None else None
        for row in reader:
            if not row:
                continue
            line = reader.line_num
            if len(rows) == MAX_ROWS:
                raise UploadError(f"CSV vượt giới hạn {MAX_ROWS:,} dòng dữ liệu.")
            if len(row) != len(header):
                raise UploadError(f"Dòng {line} có sai số cột.")
            values = []
            for feature, position in zip(features, positions):
                cell = row[position].strip()
                if cell in {"", "na"}:
                    values.append(math.nan)
                    continue
                if NUMBER.fullmatch(cell):
                    numeric = float(cell)
                    if math.isfinite(numeric) and abs(numeric) <= MAX_FLOAT32:
                        values.append(numeric)
                        continue
                raise UploadError(f"Dòng {line}, cột {feature} cần số hữu hạn hoặc na.")
            if labels is not None:
                value = row[target].strip()
                if value not in ("pos", "neg"):
                    raise UploadError(f"Dòng {line}, cột class phải là pos hoặc neg.")
                labels.append(int(value == "pos"))
            rows.append(values)
    except UnicodeDecodeError as exc:
        raise UploadError("CSV phải dùng mã hóa UTF-8.") from exc
    except csv.Error as exc:
        raise UploadError("CSV có dấu phân cách hoặc dấu ngoặc kép không hợp lệ.") from exc
    if not rows:
        raise UploadError("CSV chưa có dòng dữ liệu.")
    return rows, labels


def verified_bytes(path, expected):
    if not path.is_file():
        raise CheckpointError(f"Thiếu tệp nội bộ {path.name}.")
    payload = path.read_bytes()
    if sha256(payload).hexdigest() != expected:
        raise CheckpointError(f"SHA-256 sai lệch ở {path.name}.")
    return payload


def read_release(root=ROOT):
    try:
        pointer = json.loads((root / "configs/scania/live_model.json").read_text(encoding="utf-8"))
        folder = root / CHECKPOINT_DIR
        manifest = json.loads(verified_bytes(folder / "manifest.json", pointer["manifest_sha256"]))
        metadata = json.loads(verified_bytes(folder / "model_metadata.json", manifest["model_metadata.json"]))
        schema = json.loads(verified_bytes(folder / "feature_schema.json", manifest["feature_schema.json"]))
        model = verified_bytes(folder / "random_forest.joblib", manifest["random_forest.joblib"])
        if metadata["preprocessor"]["path"] != PREPROCESSOR or metadata["model_version"] != CHECKPOINT:
            raise CheckpointError("Tham chiếu checkpoint hoặc preprocessor không hợp lệ.")
        preprocessor = verified_bytes(root / PREPROCESSOR, metadata["preprocessor"]["sha256"])
        env = metadata["package_versions"]
        if platform.python_version() != env["python"]:
            raise CheckpointError(f"Live Prediction cần Python {env['python']} theo lockfile.")
        for package in ("numpy", "scipy", "scikit-learn", "joblib", "threadpoolctl"):
            if version(package) != env["packages"][package]:
                raise CheckpointError(f"Phiên bản {package} sai lệch. Cài lockfile Phase 2.")
        from .contracts import FEATURES

        if list(FEATURES) != schema["features"] or metadata["validation_verification"]["status"] != "PASS":
            raise CheckpointError("Schema hoặc đối chiếu Validation không hợp lệ.")
    except (OSError, ValueError, KeyError, TypeError, ImportError) as exc:
        raise CheckpointError("Live Prediction chưa sẵn sàng. Kiểm tra checkpoint và lockfile Phase 2.") from exc
    return metadata, schema["features"], model, preprocessor


def predict_csv(payload):
    metadata, features, model_data, preprocessor_data = read_release()
    rows, labels = parse_csv(payload, features)
    import joblib
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier

    model = joblib.load(io.BytesIO(model_data))
    preprocessor = joblib.load(io.BytesIO(preprocessor_data))
    if (
        not isinstance(model, RandomForestClassifier)
        or model.get_params() != metadata["parameters"]
        or list(model.classes_) != [0, 1]
        or model.n_features_in_ != len(features)
    ):
        raise CheckpointError("Mô hình nội bộ không khớp metadata.")
    scores = model.predict_proba(preprocessor.transform(np.asarray(rows, dtype=np.float64)))[:, 1]
    if not np.isfinite(scores).all() or not np.all((0 <= scores) & (scores <= 1)):
        raise CheckpointError("Checkpoint trả về điểm dự đoán không hợp lệ.")
    return {
        "model_version": metadata["model_version"],
        "threshold": metadata["threshold"],
        "scores": scores.tolist(),
        "labels": labels,
    }
