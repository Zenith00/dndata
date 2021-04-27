import seaborn as sns
import pathlib
import matplotlib.pyplot as plt

f = [int(x) for x in pathlib.Path("../data/elmir").read_text().split("\n")]

ax = sns.histplot(f, binrange=(1,20), discrete=True)
mids = [rect.get_x() + rect.get_width() / 2 for rect in ax.patches]
ax.set_xticks(mids)
ax.tick_params(axis='x', rotation=30, labelsize=8)

plt.show()