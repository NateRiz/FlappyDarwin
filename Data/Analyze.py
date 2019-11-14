import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd

sns.set_style("darkgrid")

cwd = os.getcwd()

elite = []
tournament = []
lexicase = []
roulette = []

with open(os.path.join(cwd, "Elite_16-96", "analytics.txt"), "r") as file:
    for line in file.readlines():
        elite.append(float(line))

with open(os.path.join(cwd, "Tournament_16-96", "analytics.txt"), "r") as file:
    for line in file.readlines():
        tournament.append(float(line))

with open(os.path.join(cwd, "Lexicase_16-96", "analytics.txt"), "r") as file:
    for line in file.readlines():
        lexicase.append(float(line))

with open(os.path.join(cwd, "Roulette_16-96", "analytics.txt"), "r") as file:
    for line in file.readlines():
        roulette.append(float(line))

plt.title("Selection Schemes")
rng = max([len(lexicase), len(elite), len(tournament), len(roulette)])
data = pd.DataFrame(list(zip([(i - 1) // 100 * 100 + 50 for i in range(rng)], tournament, elite, lexicase, roulette)))

data.columns = ("Generation", "Tournament", "Elite", "Lexicase", "Roulette")

ax = sns.lineplot(x="Generation", y="Tournament", data=data, ci='sd', label="Tournament")
ax = sns.lineplot(x="Generation", y="Elite", data=data, ci='sd', label="Elite")
ax = sns.lineplot(x="Generation", y="Lexicase", data=data, ci='sd', label="Lexicase")
ax = sns.lineplot(x="Generation", y="Roulette", data=data, ci='sd', label="Roulette")
ax.legend()
plt.show()
