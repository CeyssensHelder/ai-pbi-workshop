"""Download the SQLBI Contoso V2 ready-to-use CSV set into data/raw/.

Source: https://github.com/sql-bi/Contoso-Data-Generator-V2-Data (ready-to-use-data-2024 release).
Usage: python scripts/download_contoso.py [10k|100k]
"""

import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path

import py7zr

RELEASE_URL = "https://github.com/sql-bi/Contoso-Data-Generator-V2-Data/releases/download/ready-to-use-data-2024"
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"


def main(size: str = "100k") -> None:
    url = f"{RELEASE_URL}/csv-{size}.7z"
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / f"csv-{size}.7z"
        extract_dir = Path(tmp) / "extract"
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, archive)
        with py7zr.SevenZipFile(archive) as z:
            z.extractall(extract_dir)

        csv_files = list(extract_dir.rglob("*.csv"))
        if not csv_files:
            sys.exit("No CSV files found in archive")
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        for f in csv_files:
            shutil.copy2(f, RAW_DIR / f.name.lower())
            print(f"  {f.name.lower()}  ({f.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main(*sys.argv[1:])
