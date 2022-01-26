import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import matplotlib.font_manager as font_manager
import zipfile

path = os.path.join(os.getcwd()+'/01_Plots/', "results/")
df = pd.read_csv(
    path + "04_distinct_tracker_and_frequency_tracking_requests.zip")

#archive = zipfile.ZipFile(path+ "04_distinct_tracker_and_frequency_tracking_requests.zip", 'r')
#data = archive.read('04_distinct_tracker_and_frequency_tracking_requests.csv')
#df = pd.read_csv(data)

sns.set_theme(style="whitegrid")
plt.figure(figsize=(14, 6))
ax = sns.boxplot(x="cluster", y="val",
                 hue="type", palette=["k", "w"],
                 data=df, showfliers=False)

#sns.despine(ax=ax, trim=True, offset={'left':1,'right':1,'top':1,'bottom':1})

ax.set(ylabel='Number of tracking requests & distinct trackers',
       xlabel='Clustered profiles')

font = font_manager.FontProperties(family='sans-serif',
                                   weight='bold',
                                   style='normal', size=16)
plt.legend(loc='best', frameon=False, prop=font)


plt.legend(loc='best', frameon=False, prop=font)
plt.xticks(weight='bold', fontname='sans-serif', size=16)
plt.yticks(weight='bold', fontname='sans-serif', size=16)
plt.xlabel("Clustered profiles", weight='bold', fontname='sans-serif', size=16)
plt.ylabel('Number of tracking requests & distinct trackers',
           weight='bold', fontname='sans-serif', size=16)

plt.tight_layout()
plt.savefig(path + "/04_distinct_tracker_and_frequency_tracking_requests.pdf",
            dpi=600, transparent=False,   bbox_inches='tight', format="pdf")

# ax.get_figure().savefig(path+"/04_distinct_tracker_and_frequency_tracking_requests.pdf")
# ax.get_figure().savefig(path+"/04_distinct_tracker_and_frequency_tracking_requests.png")
