"""Validate a static publish directory or Vercel prebuilt output."""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Build output directory")
    args = parser.parse_args()
    if not args.output.is_dir():
        parser.error("Build output directory does not exist")
    matches = sorted(
        str(path.relative_to(args.output))
        for path in args.output.rglob("*")
        if path.is_file() and "ballpark-estimate" in path.name.lower()
    )
    if matches:
        parser.exit(1, "Build output contains excluded assets:\n" + "\n".join(matches) + "\n")
    print("Build output asset check passed")


if __name__ == "__main__":
    main()
