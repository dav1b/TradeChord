"""Integrity verification for committed canonical and browser release artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_release(release_dir: str, repo_root: str) -> list[str]:
    """Return integrity errors for one committed release."""
    release = Path(release_dir)
    root = Path(repo_root)
    manifest_path = release / "manifest.json"
    if not manifest_path.is_file():
        return [f"missing manifest: {manifest_path}"]

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []

    matrix = manifest.get("artifacts", {}).get("matrix", {})
    matrix_path = release / matrix.get("path", "")
    if not matrix_path.is_file():
        errors.append(f"missing matrix: {matrix_path}")
    elif sha256_file(matrix_path) != matrix.get("sha256"):
        errors.append(f"matrix checksum mismatch: {matrix_path}")

    web = manifest.get("artifacts", {}).get("web", {})
    web_root = root / web.get("root", "")
    for item in web.get("files", []):
        path = web_root / item["path"]
        if not path.is_file():
            errors.append(f"missing web projection: {path}")
        elif sha256_file(path) != item["sha256"]:
            errors.append(f"web projection checksum mismatch: {path}")

    current_path = root / "web/static/data/current.json"
    if current_path.is_file():
        current = json.loads(current_path.read_text(encoding="utf-8"))
        if current.get("datasetVersion") == manifest.get("datasetVersion"):
            manifest_sha = sha256_file(manifest_path)
            if current.get("manifestSha256") != manifest_sha:
                errors.append("current.json manifestSha256 does not match active manifest")
    return errors
