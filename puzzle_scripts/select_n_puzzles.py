import bson
import json
import os
from typing import List

import more_itertools
import pandas as pd


def create_puzzle_path(theme: str, tier: str, number: int, chunk: List[str]):
    result = {
        "_id": f"{theme}|{tier}|0000-9999|1620110906065|{number}",
        "min": f"{theme}|{tier}|0000",
        "max": f"{theme}|{tier}|9999",
        "ids": chunk,
        "tier": tier,
        "theme": theme,
        "gen": 1620110906065,
    }
    return result


os.chdir("/home/janek/Documents/Projects/lilaPuzzles")

with open('puzzle_scripts/mongo_dump/puzzle2_path.bson', 'rb') as f:
    puzzle2_path = bson.decode_all(f.read())

with open('puzzle_scripts/mongo_dump/puzzle2_puzzle.bson', 'rb') as f:
    puzzle2_puzzle = bson.decode_all(f.read())

len(puzzle2_puzzle)

test_data_final = pd.read_csv("puzzle_scripts/test_data.csv")
final_test_ids = set(test_data_final["PuzzleId"].sample(200))

puzzle2_puzzle_new = []

with open("puzzle2_puzzle.jsonl", "w") as puzzle_file:
    for puzzle in puzzle2_puzzle:
        if puzzle['_id'] in final_test_ids:
            puzzle2_puzzle_new.append(puzzle)
            puzzle_file.write(json.dumps(puzzle) + "\n")

theme = "mix"
tier_good = "good"
tier_all = "all"

with open("paths_filtered_tier_good.jsonl", "w") as paths_filtered_tier_good, open(
        "paths_filtered_tier_all.jsonl", "w"
) as paths_filtered_tier_all:
    for i, chunk in enumerate(more_itertools.chunked(final_test_ids, 10)):
        paths_filtered_tier_good.write(
            json.dumps(
                create_puzzle_path(theme=theme, tier=tier_good, number=i, chunk=chunk)
            )
            + "\n"
        )
        paths_filtered_tier_all.write(
            json.dumps(
                create_puzzle_path(theme=theme, tier=tier_all, number=i, chunk=chunk)
            )
            + "\n"
        )
