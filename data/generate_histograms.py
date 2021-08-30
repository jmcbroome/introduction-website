import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
conversion = {"AL":"Alabama","AK":"Alaska","AR":"Arkansas","AZ":"Arizona","CA":"California","CO":"Colorado",
    "CT":"Connecticut","DE":"Delaware","DC":"District of Columbia","FL":"Florida","GA":"Georgia","HI":"Hawaii",
    "ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine",
    "MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana",
    "NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina",
    "ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island",
    "SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia",
    "WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming","PR":"Puerto Rico"}

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
    plt.clf()
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
        plt.savefig("display_histograms/" + conversion.get(state,state) + "_csizes.png")
        plt.clf()
make_plots()