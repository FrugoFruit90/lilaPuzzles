import random

with open("submission.txt", "w") as f:
    for i in range(2282):
        f.write(f"{int(random.normalvariate(1500,100))}\n")
