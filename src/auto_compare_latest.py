from __future__ import annotations

import argparse
from pathlib import Path

from compare_outputs import compare_files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    csv_files = sorted(output_dir.glob("*.csv"), key=lambda p: p.stat().st_mtime)

    if len(csv_files) < 2:
        raise SystemExit("Need at least two CSV files in output directory.")

    old_file = csv_files[-2]
    new_file = csv_files[-1]
    out_path = compare_files(str(old_file), str(new_file), str(output_dir))

    print(f"old file: {old_file}")
    print(f"new file: {new_file}")
    print(f"saved compare file: {out_path}")


if __name__ == "__main__":
    main()
