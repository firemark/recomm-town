#!/usr/bin/env python3
import argparse
import os
from pathlib import Path

os.environ["ASSETS"] = Path(__file__.parent) / "assets"
parser = argparse.ArgumentParser()
parser.add_argument("town", type=Path)
parser.add_argument("--match-time", type=int, default=600)
parser.add_argument("--fullscreen", action="store_true")


if __name__ == "__main__":
    args = parser.parse_args()
    from recomm_town.generic_main import run
    run(
        town=args.town,
        match_time=args.match_time,
        fullscree=args.fullscreen,
    )
