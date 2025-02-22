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
    USER_RATINGS_OLD = "08_13"
    UPDATE_USER_RATINGS = False

    replace_dict = {"fjd": "f-dunne", "fruggio": "frugofruit90", "mszczepaniak": "Szczepaniak"}

    with open(f'data/{DUMP_FOLDER_NAME}/lichess/puzzle2_round.bson', 'rb') as f:
        puzzle_attempts = pd.DataFrame(bson.decode_all(f.read()))
        puzzle_attempts["puzzle_id"] = puzzle_attempts["_id"].str.split(":", expand=True).loc[:, 1]

    with open(f'data/mongo_dump/puzzle2_round.bson', 'rb') as f:
        puzzle_attempts_fruggio = pd.DataFrame(bson.decode_all(f.read()))
        puzzle_attempts_fruggio["puzzle_id"] = puzzle_attempts_fruggio["_id"].str.split(":", expand=True).loc[:, 1]
        puzzle_attempts_fruggio['u'] = "frugofruit90"

    puzzle_attempts = pd.concat([puzzle_attempts_fruggio, puzzle_attempts], axis=0)
    puzzle_attempts["u"] = puzzle_attempts["u"].replace(replace_dict)

    users = puzzle_attempts["u"].unique()

    user_ratings_past = json.load(open(f'data/user_ratings_{USER_RATINGS_OLD}.json'))
    user_ratings_past.update(json.load(open(f'data/user_ratings_08_13.json')))
    if UPDATE_USER_RATINGS:
        user_ratings_new = get_all_user_puzzle_ratings(users)
        json.dump(user_ratings_new, open(f'data/user_ratings_{datetime.date.today()}.json', 'w'))
    else:
        user_ratings_new = {}
    user_ratings_past.update(user_ratings_new)
    user_ratings = user_ratings_past

    user_ratings_df = pd.DataFrame.from_dict(user_ratings, orient="index").rename(
        columns={"rating": "player_rating", "rd": "player_rd"})
    user_ratings_df["player_rating"] -= 200
    user_ratings_df = user_ratings_df.fillna({"player_rating": 1500, "player_rd": 500})

    puzzle_attempts = puzzle_attempts.merge(user_ratings_df, right_index=True, left_on="u")
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

    puzzle_ratings_final
    puzzle_df_test = puzzle_attempts[puzzle_attempts["puzzle_id"] == 'p0063']
    puzzle_df_test[["player_rating", "player_rd", "w"]]
#     print(sum([puzzle["no_tries"] for puzzle in puzzle_ratings_final.values()]))
#     print(sum([puzzle["no_tries"] > 15 for puzzle in puzzle_ratings_final.values()]))
#     print(sum([puzzle["rd"] < 130 for puzzle in puzzle_ratings_final.values()]))
#     print(sorted([puzzle["no_tries"] for puzzle in puzzle_ratings_final.values()]))
#
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
        open(f"data/puzzle_evaluation_{datetime.date.today()}.json", 'w'),
        indent=4
    )

puzzle_evaluation_df = pd.DataFrame.from_dict(puzzle_evaluation, orient="index")

full_eval = pd.read_csv("data/test_data.csv").reset_index()
full_eval_merged = full_eval.merge(puzzle_evaluation_df, left_on="PuzzleId", right_index=True)
full_eval_merged.loc[:, 0] = full_eval_merged.loc[:, 0].round().astype(int)
full_eval_merged.loc[:, 0].to_dict()

json.dump(
    full_eval_merged.loc[:, 0].to_dict(),
    open(f"data/eval_final_{datetime.date.today()}.json", 'w'),
    indent=4
)

full_eval_merged[["PuzzleId", 0]].to_csv(f"final_data_{datetime.date.today()}.csv", index=False)
