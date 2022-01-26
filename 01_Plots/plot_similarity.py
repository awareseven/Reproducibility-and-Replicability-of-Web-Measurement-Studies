import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os
import matplotlib.font_manager as font_manager

sns.set_theme(style="white")
path = os.path.join(os.getcwd(), "results")
raw_data = pd.read_csv(os.path.join(path, "04_grouped_similarity_www_paper.csv"))

g = sns.catplot( height=3,
    aspect=2,
    data=raw_data, kind="bar",
    x="sim", y="relative", hue="cat",
    ci="sd", palette="gray", legend_out=False)

font = font_manager.FontProperties(family='sans-serif',
                                   weight='bold',
                                   style='normal')
plt.legend(loc='best', frameon=False, prop=font)
plt.xticks(weight='bold', fontname='sans-serif')
plt.yticks(weight='bold', fontname='sans-serif')

g.despine(left=True)
g.set(ylabel='Relative frequency of pages',
      xlabel='Similarity by Jaccard index')

plt.savefig(path + "/04_grouped_similarity.pdf", dpi=600, transparent=False,  bbox_inches='tight', format="pdf")
# plt.show()
