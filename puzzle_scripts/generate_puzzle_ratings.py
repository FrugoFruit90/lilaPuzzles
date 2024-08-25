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
    frugo_data = lichess.api.user("FrugoFruit90")
    user_ratings["frugofruit90"] = frugo_data["perfs"]["puzzle"]

    return user_ratings


if __name__ == "__main__":
    DUMP_FOLDER_NAME = "dump_08_19"
    RATING_FOLDER_NAME = "user_ratings_08_19"
    UPDATE_USER_RATINGS = True

    with open(f'data/{DUMP_FOLDER_NAME}/lichess/puzzle2_round.bson', 'rb') as f:
        puzzle_attempts = pd.DataFrame(bson.decode_all(f.read()))
        puzzle_attempts["puzzle_id"] = puzzle_attempts["_id"].str.split(":", expand=True).loc[:, 1]

    with open(f'data/mongo_dump/puzzle2_round.bson', 'rb') as f:
        puzzle_attempts_fruggio = pd.DataFrame(bson.decode_all(f.read()))
        puzzle_attempts_fruggio["puzzle_id"] = puzzle_attempts_fruggio["_id"].str.split(":", expand=True).loc[:, 1]
        puzzle_attempts_fruggio['u'] = "frugofruit90"

    puzzle_attempts = pd.concat([puzzle_attempts_fruggio, puzzle_attempts], axis=0)

    with open(f'data/{DUMP_FOLDER_NAME}/lichess/user4.bson', 'rb') as f:
        users = bson.decode_all(f.read())
    if UPDATE_USER_RATINGS:
        user_ratings = get_all_user_puzzle_ratings(users)
        json.dump(user_ratings, open(RATING_FOLDER_NAME, 'w'))
    else:
        user_ratings = json.load(open(RATING_FOLDER_NAME))

    for user in user_ratings:
        user_ratings[user]["rating"] -= 200

    user_ratings_df = pd.DataFrame.from_dict(user_ratings, orient="index").rename(
        columns={"rating": "player_rating", "rd": "player_rd"})
    puzzle_attempts = puzzle_attempts.merge(user_ratings_df, right_index=True, left_on="u")
    puzzle_ratings_final = {}
    puzzle_ratings_leaderboard = {}
    puzzle_evaluation = {}

    for puzzle_id in puzzle_attempts["puzzle_id"].unique():
        puzzle_glicko2 = glicko2.Player(rating=1500, rd=500, vol=0.09)
        puzzle_df = puzzle_attempts[puzzle_attempts["puzzle_id"] == puzzle_id]
        puzzle_glicko2.update_player(
            puzzle_df["player_rating"].tolist(),
            puzzle_df["player_rd"].tolist(),
            (~puzzle_df["w"]).tolist()
        )
        puzzle_rating = {
            "rating": puzzle_glicko2.rating,
            "rd": puzzle_glicko2.rd,
            "vol": puzzle_glicko2.vol,
            "no_tries": puzzle_df.shape[0],
            "no_successes": int(puzzle_df["w"].sum())
        }
        puzzle_ratings_final[puzzle_id] = puzzle_rating
        print(sum([puzzle["no_tries"] for puzzle in puzzle_ratings_final.values()]))
        print(sum([puzzle["no_tries"] > 15 for puzzle in puzzle_ratings_final.values()]))
        print(sum([puzzle["rd"] < 130 for puzzle in puzzle_ratings_final.values()]))
        print(sorted([puzzle["no_tries"] for puzzle in puzzle_ratings_final.values()]))

        if puzzle_rating["rd"] < 130:
            puzzle_ratings_leaderboard[puzzle_id] = puzzle_rating
            puzzle_evaluation[puzzle_id] = puzzle_rating["rating"]

    json.dump(
        puzzle_ratings_final,
        open(f"data/puzzle_ratings_final_{datetime.date.today()}.json", 'w'),
        indent=4
    )

    json.dump(
        puzzle_ratings_leaderboard,
        open(f"data/puzzle_ratings_leaderboard_{datetime.date.today()}.json", 'w'),
        indent=4
    )

    json.dump(
        puzzle_evaluation,
        open(f"data/puzzle_evaluation{datetime.date.today()}.json", 'w'),
        indent=4
    )

puzzle_evaluation_df = pd.DataFrame.from_dict(puzzle_evaluation, orient="index")

full_eval = pd.read_csv("puzzle_scripts/test_data.csv").reset_index()
full_eval_merged = full_eval.merge(puzzle_evaluation_df, left_on="PuzzleId", right_index=True)
full_eval_merged.loc[:, 0] = full_eval_merged.loc[:, 0].round().astype(int)
full_eval_merged.loc[:, 0].to_dict()

json.dump(
    full_eval_merged.loc[:, 0].to_dict(),
    open(f"data/eval_final_{datetime.date.today()}.json", 'w'),
    indent=4
)
