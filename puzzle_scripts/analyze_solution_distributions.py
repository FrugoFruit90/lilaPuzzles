import bson

import pandas as pd

DUMP_FOLDER_NAME = "dump_08_26"
with open(f'data/{DUMP_FOLDER_NAME}/lichess/puzzle2_round.bson', 'rb') as f:
    puzzle_attempts = pd.DataFrame(bson.decode_all(f.read()))
    puzzle_attempts["puzzle_id"] = puzzle_attempts["_id"].str.split(":", expand=True).loc[:, 1]

puzzle_attempts["ones"] = 1
print(puzzle_attempts.groupby(pd.Grouper(key='d', freq='W-MON'))["ones"].count())

print(puzzle_attempts["ones"].sum())
grouped_solutions = puzzle_attempts.groupby("puzzle_id")["ones"].sum()
grouped_solutions["buckets"] = pd.cut(grouped_solutions, [0, 6, 7, 8 , 10, 20, 100])
print(grouped_solutions["buckets"].value_counts(sort=False))
