import argparse
from update_us_states import update_us_states
from generate_display_tables import generate_display_tables
from datetime import date, timedelta
import subprocess

conversion = {"AL":"Alabama","AK":"Alaska","AR":"Arkansas","AZ":"Arizona","CA":"California","CO":"Colorado",
    "CT":"Connecticut","DE":"Delaware","DC":"District of Columbia","FL":"Florida","GA":"Georgia","HI":"Hawaii",
    "ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine",
    "MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana",
    "NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina",
    "ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island",
    "SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia",
    "WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming","PR":"Puerto Rico"}

parser = argparse.ArgumentParser()
parser.add_argument("-i","--input",help="Path to the protobuf file to update the website to display. Must include samples from within the last month.")
parser.add_argument("-m","--metadata",help="Path to a metadata file matching the targeted protobuf to update the website to display.")
parser.add_argument("-f","--reference",help="Path to a reference fasta.")
parser.add_argument("-a","--annotation",help="Path to a gtf annotation matching the reference.")
parser.add_argument("-t","--threads",type=int,help="Number of threads to use.", default = 4)
parser.add_argument("-X","--lookahead",type=int,help="Number to pass to parameter -X of introduce. Increase to merge nested clusters. Default 2", default = 2)
args = parser.parse_args()
pbf = args.input
mf = args.metadata
print("Identifying state samples.")
subprocess.check_call("matUtils extract -i " + pbf + " -u samplenames.txt",shell=True)
badsamples = open("unlabeled_samples.txt","w+")
with open("samplenames.txt") as inf:
    with open("sample_regions.tsv","w+") as outf:
        for entry in inf:
            country = entry.split("/")[0]
            if country == "USA":
                state = entry.split("/")[1].split("-")[0]
                if state in conversion:
                    print(entry.strip(), state, file = outf)
                else:
                    print(entry.strip(), file = badsamples)
badsamples.close()
print("Clearing out unparseable USA samples.")
subprocess.check_call("matUtils extract -i " + pbf + " -s unlabeled_samples.txt -p -o clean.pb", shell = True)
print("Calling introduce.")
subprocess.check_call("matUtils introduce -i clean.pb -s sample_regions.tsv -u hardcoded_clusters.tsv -T " + str(args.threads) + " -X " + str(args.lookahead), shell=True)
print("Updating map display data.")
update_us_states()
print("Generating top cluster tables.")
generate_display_tables()
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
subprocess.check_call("matUtils extract -i clean.pb -M clusterswapped.tsv --write-taxodium cview.pb --title Cluster-Tracker -g " + args.annotation + " -f " + args.reference,shell=True)
print("Process completed; check website for results.")