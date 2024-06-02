import datetime

import bson
import glicko2
import json
import lichess.api
import pandas as pd


def get_all_user_puzzle_ratings(users: list):
    user_ratings = {}
    for user in users:
        try:
            user_data = lichess.api.user(user["_id"])
            if user_data.get("disabled", None):
                print(f"User {user['_id']} is banned!")
                continue
            rating_dict = user_data["perfs"].get("puzzle", {"games": 0})
            if rating_dict["games"] < 25:
                print(f"User {user['_id']} doesn't have enough games")
            else:
                user_ratings[user["_id"]] = rating_dict
        except lichess.api.ApiHttpError:
            print(f"User {user['_id']} doesn't have a lichess account!")
    return user_ratings


if __name__ == "__main__":
    STARTING_RATING = {"rating": 1500, "ratingDeviation": 100}
    DUMP_FOLDER_NAME = "dump_24_06_02"
    UPDATE_USER_RATINGS = False

    with open(f'data/{DUMP_FOLDER_NAME}/lichess/puzzle2_round.bson', 'rb') as f:
        puzzle_attempts = pd.DataFrame(bson.decode_all(f.read()))
        puzzle_attempts["puzzle_id"] = puzzle_attempts["_id"].str.split(":", expand=True).loc[:, 1]

    with open(f'data/{DUMP_FOLDER_NAME}/lichess/user4.bson', 'rb') as f:
        users = bson.decode_all(f.read())
    if UPDATE_USER_RATINGS:
        user_ratings = get_all_user_puzzle_ratings(users)
        json.dump(user_ratings, open("data/user_ratings.json", 'w'))
    else:
        user_ratings = json.load(open("data/user_ratings.json"))

    user_ratings_df = pd.DataFrame.from_dict(user_ratings, orient="index").rename(
        columns={"rating": "player_rating", "rd": "player_rd"})
    puzzle_attempts = puzzle_attempts.merge(user_ratings_df, right_index=True, left_on="u")
    puzzle_ratings_final = {}

    for puzzle_id in puzzle_attempts["puzzle_id"].unique():
        puzzle_glicko2 = glicko2.Player(rating=1500, rd=500, vol=0.09)
        puzzle_df = puzzle_attempts[puzzle_attempts["puzzle_id"] == puzzle_id]
        puzzle_glicko2.update_player(
            puzzle_df["player_rating"].tolist(),
            puzzle_df["player_rd"].tolist(),
            (~puzzle_df["w"]).tolist()
        )
        puzzle_ratings_final[puzzle_id] = {
            "rating": puzzle_glicko2.rating,
            "rd": puzzle_glicko2.rd,
            "vol": puzzle_glicko2.vol,
            "no_tries": puzzle_df.shape[0],
            "no_successes": int(puzzle_df["w"].sum())
        }

    json.dump(
        puzzle_ratings_final,
        open(f"data/puzzle_ratings_final_{datetime.date.today()}.json", 'w'),
        indent=4
    )
