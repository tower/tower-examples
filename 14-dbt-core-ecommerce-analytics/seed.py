from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse
from urllib.request import urlopen

import boto3


class SeedDownloadError(RuntimeError):
    """Raised when the seed archive cannot be retrieved or processed."""


def _download_to_path(uri: str, destination: Path) -> None:
    parsed = urlparse(uri)
    if parsed.scheme == "s3":
        bucket = parsed.netloc
        key = parsed.path.lstrip("/")
        if not bucket or not key:
            raise SeedDownloadError(f"Invalid S3 URI: {uri}")
        client = boto3.client("s3")
        try:
            client.download_file(bucket, key, str(destination))
        except Exception as exc:  # pylint: disable=broad-except
            raise SeedDownloadError(f"Failed to download {uri}: {exc}") from exc
    else:
        try:
            with urlopen(uri) as response, open(destination, "wb") as fh:  # type: ignore[arg-type]
                shutil.copyfileobj(response, fh)
        except Exception as exc:  # pylint: disable=broad-except
            raise SeedDownloadError(f"Failed to download {uri}: {exc}") from exc


def _log_seed_files(seeds_dir: Path, files: Iterable[Path]) -> None:
    paths = ", ".join(sorted(str(f.resolve()) for f in files)) or "<none>"
    print(f"[tower-dbt] Seeds populated in {seeds_dir.resolve()}: {paths}")


def populate_seeds_from_archive(uri: str, seeds_dir: Path) -> None:
    """
    Populate `seeds_dir` with CSV files extracted from the zipped archive at `uri`.

    Existing CSVs are removed before new files are copied in.
    """
    seeds_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = Path(tmpdir) / "seeds.zip"
        extract_dir = Path(tmpdir) / "extract"
        extract_dir.mkdir(parents=True, exist_ok=True)

        _download_to_path(uri, archive_path)

        try:
            with zipfile.ZipFile(archive_path) as zf:
                zf.extractall(extract_dir)
        except zipfile.BadZipFile as exc:
            raise SeedDownloadError(f"Seed archive is not a valid zip: {uri}") from exc

        csv_files = list(extract_dir.rglob("*.csv"))
        if not csv_files:
            raise SeedDownloadError(f"Seed archive {uri} did not contain any CSV files")

        for existing in seeds_dir.glob("*.csv"):
            existing.unlink()

        copied: list[Path] = []
        for src in csv_files:
            dest = seeds_dir / src.name
            shutil.copy2(src, dest)
            copied.append(dest)

        _log_seed_files(seeds_dir, copied)
