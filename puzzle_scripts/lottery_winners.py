import bson
import os
import random

import pandas as pd

# os.getcwd()
# os.chdir("../..")

DUMP_FOLDER_NAME = "dump_31_08"

with open(f'data/{DUMP_FOLDER_NAME}/lichess/puzzle2_round.bson', 'rb') as f:
    puzzle_attempts = pd.DataFrame(bson.decode_all(f.read()))
    puzzle_attempts["puzzle_id"] = puzzle_attempts["_id"].str.split(":", expand=True).loc[:, 1]

puzzle_attempts["ones"] = 1
print(puzzle_attempts.columns)
user_counts = puzzle_attempts[puzzle_attempts["d"] > "2024-08-11 00:00:00.000"].groupby("u")["ones"].count()
print(user_counts[user_counts >= 300])
gods = user_counts[user_counts >= 300].index.to_list()
print(gods)
print(random.sample(gods, k=3))