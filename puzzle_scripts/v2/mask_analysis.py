import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error

def main():
    # Load data
    puzzle_rating_df = pd.read_json('data/puzzle_ratings_final_2025-02-24.json', orient='index')[[
        "rating", "no_tries", "no_successes", "rd"]]
    puzzle_df = pd.read_csv('data/puzzle_ratings_final_2025-02-24.csv')
    mask_df = pd.read_csv('data/mask_final_submissions_2025.csv').iloc[:, 1:]
    top9 = mask_df.columns
    mask_df = mask_df.add_prefix("masks_")
    submission_df = pd.read_csv('data/rating_final_submissions_2025.csv').rename({"DML": "davidmingliu"}, axis=1)
    submission_df = submission_df[top9]
    submission_df = submission_df.add_prefix("ratings_")

    # print(puzzle_df.shape)
    # print(puzzle_df.columns)
    # print(mask_df.shape)
    # print(mask_df.columns)
    # print(submission_df.shape)
    # print(submission_df.columns)

    merged_df = pd.concat([puzzle_df, mask_df, submission_df], axis=1).set_index("PuzzleId")
    merged_df = merged_df.join(puzzle_rating_df, lsuffix='_rat', rsuffix='_prep')
    print(merged_df.shape)
    print(merged_df.columns)

    team_rating_cols = [c for c in merged_df.columns if c.startswith("ratings_")]
    team_mask_cols = [c for c in merged_df.columns if c.startswith("masks_")]

    leaderboard_df = merged_df[merged_df["public_leaderboard"] == 1]
    holdout_df = merged_df[merged_df["public_leaderboard"] == 1]

    results = []

    for df in [leaderboard_df]:
        for team in team_rating_cols:
            team_name = team.replace("ratings_", "")
            preds = df[team]
            truth = df['rating_rat']

            # per-puzzle squared error
            se = (preds - truth) ** 2

            # baseline MSE
            baseline = se.mean()

            # compute team mask column
            mask_col = f"masks_{team_name}"
            if mask_col in df:
                mask = (df[mask_col].fillna(0).astype(int) == 1)
            else:
                mask = np.zeros(len(df), dtype=bool)

            # New score
            new_se = se.copy()
            new_se.loc[mask] = 0.0
            new_score = new_se.mean()

            # Perfect score = mask top 10% highest SE
            top_k = int(len(se) * 0.1)
            top_idx = se.nlargest(top_k).index
            perfect_se = se.copy()
            perfect_se.loc[top_idx] = 0.0
            perfect_score = perfect_se.mean()

            # Uncertainty ratio
            ur = new_score / perfect_score if perfect_score > 0 else np.nan

            results.append({
                "team": team_name,
                "baseline_mse": baseline,
                "new_score": new_score,
                "perfect_score": perfect_score,
                "UR": ur
            })

        df_results = pd.DataFrame(results)
        print(df_results.sort_values("UR"))

if __name__ == "__main__":
    main()
