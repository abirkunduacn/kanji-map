import gzip
import shutil
import urllib.request
from pathlib import Path

from scripts.sources import SOURCES, RAW_DIR


def _download(url: str, dest: Path, is_gzip: bool) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    print(f"Downloading {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "kanji-mindmap-build"})
    with urllib.request.urlopen(req) as resp, open(tmp, "wb") as fh:
        shutil.copyfileobj(resp, fh)
    if is_gzip:
        with gzip.open(tmp, "rb") as gz, open(dest, "wb") as out:
            shutil.copyfileobj(gz, out)
        tmp.unlink()
    else:
        tmp.replace(dest)
    print(f"  -> {dest} ({dest.stat().st_size} bytes)")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for s in SOURCES:
        if s["dest"].exists():
            print(f"Skip (exists): {s['dest']}")
            continue
        _download(s["url"], s["dest"], s["gzip"])


if __name__ == "__main__":
    main()
