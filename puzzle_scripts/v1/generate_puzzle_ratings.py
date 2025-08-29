import datetime

import bson
import json

import glicko2
import lichess.api
import pandas as pd


def get_all_user_puzzle_ratings(users: list):
    user_ratings = {}
    for user in users:
        try:
            user_data = lichess.api.user(user)
            if user_data.get("disabled", None):
                print(f"User {user} is banned!")
                continue
            rating_dict = user_data["perfs"].get("puzzle", {"games": 0})
            if rating_dict["games"] < 1:
                print(f"User {user} doesn't have enough games")
                user_ratings[user] = rating_dict
            else:
                user_ratings[user] = rating_dict
        except lichess.api.ApiHttpError:
            print(f"User {user} doesn't have a lichess account!")
    frugo_data = lichess.api.user("FrugoFruit90")
    user_ratings["frugofruit90"] = frugo_data["perfs"]["puzzle"]

    return user_ratings


if __name__ == "__main__":
    DUMP_FOLDER_NAME = "dump_25_01_30"
    USER_RATINGS_OLD = "user_ratings_2025-02-23.json"
    UPDATE_USER_RATINGS = False

    replace_dict = {"fjd": "f-dunne", "fruggio": "frugofruit90", "mszczepaniak": "Szczepaniak"}

    with open(f'data/{DUMP_FOLDER_NAME}/lichess/puzzle2_round.bson', 'rb') as f:
        puzzle_attempts = pd.DataFrame(bson.decode_all(f.read()))
        puzzle_attempts["puzzle_id"] = puzzle_attempts["_id"].str.split(":", expand=True).loc[:, 1]

    final_ids = puzzle_attempts["puzzle_id"]

    with open(f'data/mongo_dump/puzzle2_round.bson', 'rb') as f:
        p_a_f = pd.DataFrame(bson.decode_all(f.read()))
        p_a_f["puzzle_id"] = p_a_f["_id"].str.split(":", expand=True).loc[:, 1]
        p_a_f['u'] = "frugofruit90"
        p_a_f = p_a_f[p_a_f["puzzle_id"].isin(puzzle_attempts["puzzle_id"].unique())]

    puzzle_attempts = pd.concat([p_a_f, puzzle_attempts], axis=0)
    puzzle_attempts["u"] = puzzle_attempts["u"].replace(replace_dict)

    users = puzzle_attempts["u"].unique()

    user_ratings_past = json.load(open(f'data/{USER_RATINGS_OLD}'))
    user_ratings_past.update(json.load(open(f'data/user_ratings_08_13.json')))
    if UPDATE_USER_RATINGS:
        user_ratings_new = get_all_user_puzzle_ratings(users)
        json.dump(user_ratings_new, open(f'data/{datetime.date.today()}', 'w'))
    else:
        user_ratings_new = {}
    user_ratings_past.update(user_ratings_new)
    user_ratings = user_ratings_past

    user_ratings_df = pd.DataFrame.from_dict(user_ratings, orient="index").rename(
        columns={"rating": "player_rating", "rd": "player_rd"})
    puzzle_attempts = puzzle_attempts.merge(user_ratings_df, how="left", right_index=True, left_on="u")
    print(f"Total attempts: {puzzle_attempts.shape[0]}")
    print(f"{puzzle_attempts["player_rating"].isnull().sum()} attempts don't have rating applied")
    puzzle_attempts["player_rating"] = puzzle_attempts["player_rating"].fillna(1500.0)
    puzzle_attempts["player_rating"] -= 200
    puzzle_attempts["player_rd"] = puzzle_attempts["player_rd"].fillna(500.0)
    puzzle_ratings_final = {}
    puzzle_ratings_leaderboard = {}
    puzzle_evaluation = {}

    for puzzle_id in puzzle_attempts["puzzle_id"].unique():
        puzzle_glicko2 = glicko2.Player(rating=1500, rd=500, vol=0.09)
        puzzle_df = puzzle_attempts[puzzle_attempts["puzzle_id"] == puzzle_id]
        for i, attempt in puzzle_df.iterrows():
            puzzle_glicko2.update_player(
                [attempt['player_rating']],
                [attempt['player_rd']],
                [not attempt["w"]]
            )
        puzzle_rating = {
            "rating": puzzle_glicko2.rating,
            "rd": puzzle_glicko2.rd,
            "vol": puzzle_glicko2.vol,
            "no_tries": puzzle_df.shape[0],
            "no_successes": int(puzzle_df["w"].sum())
        }
        puzzle_ratings_final[puzzle_id] = puzzle_rating
        puzzle_ratings_leaderboard[puzzle_id] = puzzle_rating
        puzzle_evaluation[puzzle_id] = puzzle_rating["rating"]

    # After the last iteration
    puzzle_evaluation_df = pd.DataFrame.from_dict(puzzle_ratings_final,
                                                  orient="index",
                                                  columns=["rating", "rd", "no_tries", "no_successes"]).round().astype(int)
    full_eval = pd.read_csv("data/test_data.csv")
    full_eval_merged = full_eval.merge(puzzle_evaluation_df, left_on="PuzzleId", right_index=True)
    full_eval_merged.to_csv(f"data/final_data_{datetime.date.today()}.csv", index=False)
