import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
def make_plots():
    cdf = pd.read_csv("hardcoded_clusters.tsv",sep='\t')
    bins = [1,10,50,100,500,1000,10000]
    counts,xb = np.histogram(cdf.sample_count,bins=bins)
    ax = sns.barplot(x=xb[:-1],y=np.log10(counts),color='blue')
    ax.set_xlabel("Cluster Sizes")
    ax.set_xticklabels([str(b) + "+" for b in xb[:-1]])
    ax.set_ylabel("Count")
    yticks = [1,2,3,4]
    ax.set_yticks(yticks)
    ax.set_yticklabels([str(int(10**y)) for y in yticks])
    plt.savefig("display_histograms/default_csizes.png")

    for state, clusters in cdf.groupby("region"):
        print("Generating figure for state " + state)
        bins = [1,10,50,100,500,1000,10000]
        counts,xb = np.histogram(clusters.sample_count,bins=bins)
        ax = sns.barplot(x=xb[:-1],y=np.log10(counts),color='blue')
        ax.set_xlabel("Cluster Sizes")
        ax.set_xticklabels([str(b) + "+" for b in xb[:-1]])
        ax.set_ylabel("Count")
        yticks = [1,2,3,4]
        ax.set_yticks(yticks)
        ax.set_yticklabels([str(int(10**y)) for y in yticks])
        plt.savefig("display_histograms/" + state + "_csizes.png")
make_plots()