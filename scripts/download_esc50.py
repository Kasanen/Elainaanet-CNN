"""T02: lataa ESC-50, pura eläinluokat ja tarkista 400 leikettä.

Ajo repon juuresta:
    python scripts/download_esc50.py                 # data/ESC-50
    python scripts/download_esc50.py --data-dir /content/drive/MyDrive/Elainaanet-CNN/data
"""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # jotta `src` löytyy

from src.data import ANIMAL_CLASSES, check_dataset, download_esc50, load_metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--url", default=None, help="vaihtoehtoinen zip-osoite (oletus GitHub)")
    args = parser.parse_args()

    root = download_esc50(args.data_dir, **({"url": args.url} if args.url else {}))
    df = load_metadata(args.data_dir)
    check_dataset(df)

    print(f"OK: {len(df)} leikettä kansiossa {root}")
    print("Leikkeitä per luokka:")
    counts = df["target"].value_counts().sort_index()
    for target, n in counts.items():
        print(f"  {target}  {ANIMAL_CLASSES[target]:<8} {n}")
    print("Leikkeitä per foldi:", df["fold"].value_counts().sort_index().to_dict())


if __name__ == "__main__":
    main()
