import pandas as pd
import pandas.io.json
import toml
import pathlib
import collections as clc
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


successions = clc.defaultdict(int) | {
   "OLpEErtXmSdKY4OH": 1187 # Final Damage of Haak -> Van
}
def vis(party):

   players = pd.read_csv(f"./{party}_players.csv")
   damage = pd.read_csv(f"./{party}.csv")

   player_damage = damage.merge(players, how="left",on="Actor ID")#.pivot(index="session",columns="Player Name",values="damage")
   player_damage["damage"].to_frame().apply(lambda x: print(x, end="\n\n"), axis=1)

   player_damage["damage"] = player_damage["damage"].to_frame().apply(lambda x: x["damage"] + successions[player_damage.iloc[x.name]["Actor ID"]], axis=1)
   print(player_damage)
   ax = sns.lineplot(data=player_damage, x="session",y="damage",hue="Player Name", legend="brief")
   plt.legend(bbox_to_anchor=(1.0, 1), loc='upper left')
   ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

   fig = plt.gcf()
   fig.set_size_inches(12.5, 6.5)

   plt.show()

vis("purple")
