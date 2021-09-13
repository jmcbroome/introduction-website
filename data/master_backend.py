import argparse
from update_js import update_js
from generate_display_tables import generate_display_tables
from datetime import date, timedelta
import subprocess

def read_lexicon(lfile):
    conversion = {}
    with open(lfile) as inf:
        for entry in inf:
            spent = entry.strip().split(",")
            for alternative in spent:
                conversion[alternative] = spent[0]
    return conversion

def parse_setup():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input",help="Path to the protobuf file to update the website to display.")
    parser.add_argument("-s","--sample_regions",help="Path to a two-column tsv containing sample names and associated regions.")
    parser.add_argument("-j","--geojson",help="Path to a geojson to use.")
    parser.add_argument("-m","--metadata",help="Path to a metadata file matching the targeted protobuf to update the website to display.")
    parser.add_argument("-f","--reference",help="Path to a reference fasta.")
    parser.add_argument("-a","--annotation",help="Path to a gtf annotation matching the reference.")
    parser.add_argument("-t","--threads",type=int,help="Number of threads to use.", default = 4)
    parser.add_argument("-l","--lexicon",help="Optionally, link to a text file containing all names for the same region, one region per row, tab separated.", default = "")
    parser.add_argument("-X","--lookahead",type=int,help="Number to pass to parameter -X of introduce. Increase to merge nested clusters. Default 2", default = 2)
    args = parser.parse_args()
    return args

def primary_pipeline(args):
    pbf = args.input
    mf = args.metadata
    if args.lexicon != "":
        conversion = read_lexicon(args.lexicon)
    else:
        conversion = {}
    # print(conversion)
    print("Calling introduce.")
    subprocess.check_call("matUtils introduce -i " + args.input + " -s " + args.sample_regions + " -u hardcoded_clusters.tsv -T " + str(args.threads) + " -X " + str(args.lookahead), shell=True)
    print("Updating map display data.")
    update_js(args.geojson, conversion)
    print("Generating top cluster tables.")
    generate_display_tables(conversion)
    print("Preparing taxodium view.")
    sd = {}
    with open("cluster_labels.tsv") as inf:
        for entry in inf:
            spent = entry.strip().split()
            if spent[0] == "sample":
                continue
            sd[spent[0]] = spent[1]

    with open(mf) as inf:
        with open("clusterswapped.tsv","w+") as outf:
            #clusterswapped is the same as the metadata input
            #except with the country column updated. 
            for entry in inf:
                spent = entry.strip().split("\t")                
                if spent[0] in sd:
                    spent[3] = sd[spent[0]]
                print("\t".join(spent),file=outf)
    print("Generating viewable pb.")
    subprocess.check_call("matUtils extract -i " + args.input + " -M clusterswapped.tsv --write-taxodium cview.pb --title Cluster-Tracker -g " + args.annotation + " -f " + args.reference,shell=True)
    print("Process completed; check website for results.")

if __name__ == "__main__":
    primary_pipeline(parse_setup())