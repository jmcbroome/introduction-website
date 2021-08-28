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
args = parser.parse_args()
pbf = args.input
#print("Clearing out old data files.")
# try:
#     subprocess.check_call("rm display_json/*context.json",shell=True)
#     subprocess.check_call("rm display_tables/*.tsv",shell=True)
#     subprocess.check_call("rm hardcoded_clusters.tsv",shell=True)
# except:
#     continue
print("Identifying state samples.")
subprocess.check_call("matUtils extract -i " + pbf + " -u samplenames.txt",shell=True)
with open("samplenames.txt") as inf:
    with open("sample_regions.tsv","w+") as outf:
        for entry in inf:
            country = entry.split("/")[0]
            if country == "USA":
                state = entry.split("/")[1].split("-")[0]
                if state in conversion:
                    print(entry.strip(), state, file = outf)
print("Calling introduce.")
# subprocess.check_call("matUtils introduce -i " + pbf + " -s sample_regions.tsv -L \"" + str(date.today()-timedelta(days=30)) + "\" -u hardcoded_clusters.tsv -o full_output.tsv -T 4", shell=True)
print("Updating map display data.")
update_us_states()
print("Generating top cluster tables and setting up json extraction.")
generate_display_tables()
print("Extracting JSON views.")
subprocess.check_call("matUtils extract -i " + pbf + " -K extraction_targets.txt:50 -M cluster_labels.tsv", shell=True)
subprocess.check_call("mv *context.json display_json/",shell=True)
print("Process completed; check website for results.")