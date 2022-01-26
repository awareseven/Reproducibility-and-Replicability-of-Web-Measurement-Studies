import argparse
import matplotlib.pyplot as plt
import numpy as np
import sys
import pandas as pd
from itertools import zip_longest
import seaborn as sns
from PIL.ImageColor import colormap


def main(input_fname, output_fname):
    df = pd.read_csv(input_fname, sep=',')
    #x = df[['Conference', 'Year', 'Number_Analyzed_Papers']]
    
    years = sorted(df['Year'].unique())
    confs = sorted(df['Conference'].unique())

    # this should work with df.groupby as well :/    
    def gen():
        for c in confs:
            yield df.loc[df['Conference'] == c]['Number_Analyzed_Papers'].array[::-1]

    X = list(zip_longest(*gen(), fillvalue=0))
    X = pd.DataFrame(X, columns=confs, index=years)
    X = X.reindex(sorted(X.columns)[::-1], axis=1)

    X.plot.barh(stacked=True, figsize=(6, 2.3), xlim=(0,40))
    sns.despine()
    plt.legend(loc='lower right', prop={'weight':'bold'}) 
    plt.xticks(weight='bold', fontname='sans-serif')
    plt.yticks(weight='bold', fontname='sans-serif')

    plt.xlabel("Number of analyzed papers", weight='bold', fontname='sans-serif')
    plt.ylabel("Year of publication", weight='bold', fontname='sans-serif')
    plt.tight_layout()
    plt.savefig(output_fname)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("data", metavar="CSV", action="store", type=str,
                        help="The data to plot.")
    parser.add_argument("output", metavar="OUT", action="store", type=str,
                        help="The file to plot to. This also specifies the output type.")

    args = parser.parse_args()
    sys.exit(main(args.data, args.output))
