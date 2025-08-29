import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error

# matplotlib.use('TkAgg')

masks = dict()
submissions = dict()



for _dir in os.listdir('.'):
    if _dir.__contains__("."):
        continue
    dir_path = os.path.join('.', _dir)

    mask_path = os.path.join(dir_path, 'mask.txt')
    if os.path.exists(mask_path):
        masks[_dir] = pd.read_csv(mask_path, header=None)

    submissions[_dir] = []

    for i in range(1, 4):
        submission_path = os.path.join(dir_path, f'submission{i}.txt')
        if os.path.exists(submission_path):
            submissions[_dir].append(pd.read_csv(submission_path, header=None))

# masks_df = pd.DataFrame.from_dict(masks, orient='index')
# masks_df.to_csv('../competition_compilation.csv', index=False)

testing_data = pd.read_csv('../../testing_data.csv')
testing_targets = testing_data['rating']
testing_leaderboard_bools = testing_data['public_leaderboard']

public_leaderboard = testing_targets[testing_data['public_leaderboard']]
private_holdout = testing_targets[testing_data['public_leaderboard'] == False]

print("Final:")

for name in submissions:
    print(name, ': ')
    for i in range(len(submissions[name])):
        submission = submissions[name][i]
        submission_holdout = submission[testing_data['public_leaderboard'] == False]

        score = mean_squared_error(private_holdout, submission_holdout)

        print("Submission", i+1, ': ', score)

print()



print("Final with mask:")

for name in submissions:
    print(name, ': ')
    for i in range(len(submissions[name])):
        submission = submissions[name][i]
        submission_with_mask = submission.copy()
        submission_with_mask.loc[masks[name][0] == 1, 0] = testing_targets[masks[name][0] == 1]
        submission_holdout = submission_with_mask[testing_data['public_leaderboard'] == False]

        score = mean_squared_error(private_holdout, submission_holdout)

        print("Submission", i+1, ': ', score)

# print(testing_targets)

print("Final with perfect mask:")

for name in submissions:
    print(name, ': ')
    for i in range(len(submissions[name])):
        submission = submissions[name][i]
        # print(testing_targets)
        deltas = submission.subtract(testing_targets, axis=0)
        errors = deltas.abs()
        top_errors = errors.squeeze().argsort()[-223:]
        # print(deltas.loc[top_errors])

        perfect_mask = pd.Series(np.zeros(2235))
        perfect_mask.loc[top_errors] = 1
        # print(perfect_mask)
        # print(type(deltas))
        # print(deltas)

        submission_with_mask = submission.copy()
        submission_with_mask.loc[perfect_mask == 1, 0] = testing_targets[perfect_mask == 1]
        submission_holdout = submission_with_mask[testing_data['public_leaderboard'] == False]

        score = mean_squared_error(private_holdout, submission_holdout)

        print("Submission", i + 1, ': ', score)
