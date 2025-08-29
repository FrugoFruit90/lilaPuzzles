import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit

# Temporarily expand Pandas display settings
pd.set_option("display.max_rows", None)  # Show all rows
pd.set_option("display.max_columns", None)  # Show all columns
pd.set_option("display.width", 0)  # Prevent line wrapping

df = pd.read_csv("data/final_data_2025-02-24.csv")

print(df[df["no_successes"] == 0].shape[0])

df = df[df["no_successes"] > 0]
# Define bin edges from 0 to 3000 with step of 100
bins = np.arange(0, 3100, 100)

# Plot histogram
plt.figure(figsize=(10, 6))
plt.hist(df['rating'], bins=bins, edgecolor='black', alpha=0.7)
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.title('Histogram with Bins of 100')
plt.xticks(bins, rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

# Define stratification column:
# Option 1: Stratify by rating bins (if ratings are the target variable)
df['rating_bin'] = pd.qcut(df['rating'], q=10, labels=False, duplicates='drop')

# Option 2: Stratify by number of annotations (if they strongly influence ratings)
df['annotation_bin'] = pd.qcut(df['no_tries'], q=10, labels=False, duplicates='drop')

# Choose stratification approach (rating or annotation count)
stratify_col = 'rating_bin'  # Change to 'annotation_bin' if preferred

# Perform stratified split
sss = StratifiedShuffleSplit(n_splits=1, test_size=0.5, random_state=42)
df["public_leaderboard"] = False
df["private_holdout"] = False
for public_idx, private_idx in sss.split(df, df['rating_bin']):
    df.iloc[public_idx, df.columns.get_loc('public_leaderboard')] = True
    df.iloc[private_idx, df.columns.get_loc('private_holdout')] = True

# Fill NaN values (since only one of the columns will be set for each row)
df['public_leaderboard'] = df['public_leaderboard'].fillna(False).astype(bool)
df['private_holdout'] = df['private_holdout'].fillna(False).astype(bool)

# Drop helper column
print(df[['public_leaderboard', 'private_holdout']].value_counts())
summary = df.groupby("public_leaderboard")[["no_tries", "rating"]].describe()
print(summary)

cols_to_drop = ['rating_bin', 'rd', 'no_tries', 'no_successes', 'rating_bin', 'annotation_bin']
df['rating'] = df['rating'].astype(int)
df.drop(columns= cols_to_drop).to_csv(f"data/puzzle_ratings_final_{datetime.date.today()}.csv", index=False)