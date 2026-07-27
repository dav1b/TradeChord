import hashlib
import json

from tradechord_pipeline.verification import verify_release


def test_verify_release_covers_matrix_web_and_current(tmp_path):
    release = tmp_path / "data/releases/v1"
    web = tmp_path / "web/static/data/v1"
    release.mkdir(parents=True)
    web.mkdir(parents=True)
    matrix = release / "trade_matrix.csv.gz"
    matrix.write_bytes(b"matrix")
    country = web / "overview.json"
    country.write_bytes(b"overview")

    manifest = {
        "datasetVersion": "v1",
        "artifacts": {
            "matrix": {
                "path": matrix.name,
                "sha256": hashlib.sha256(b"matrix").hexdigest(),
            },
            "web": {
                "root": "web/static/data/v1",
                "files": [{
                    "path": "overview.json",
                    "sha256": hashlib.sha256(b"overview").hexdigest(),
                }],
            },
        },
    }
    manifest_path = release / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    current = tmp_path / "web/static/data/current.json"
    current.parent.mkdir(parents=True, exist_ok=True)
    current.write_text(json.dumps({
        "datasetVersion": "v1",
        "manifestSha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
    }), encoding="utf-8")

    assert verify_release(str(release), str(tmp_path)) == []
    country.write_bytes(b"tampered")
    assert "web projection checksum mismatch" in verify_release(
        str(release), str(tmp_path)
    )[0]
