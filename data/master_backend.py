import argparse
from update_us_states import update_us_states
from generate_display_tables import generate_display_tables
from datetime import date, timedelta
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("-i","--input",help="Path to the protobuf file to update the website to display. Must include samples from within the last month.")
args = parser.parse_args()
pbf = args.input
print("Clearing out old data files.")
# try:
#     subprocess.check_call("rm display_json/*context.json",shell=True)
#     subprocess.check_call("rm display_tables/*topclusters.tsv",shell=True)
#     subprocess.check_call("rm hardcoded_clusters.tsv",shell=True)
# except:
#     continue
print("Calling introduce.")
subprocess.check_call("matUtils introduce -i " + pbf + "-L " + str(date.today()-timedelta(days=30)) + "-u harcoded_clusters.tsv", shell=True)
print("Updating map display data.")
update_us_states()
print("Generating top cluster tables and setting up json extraction.")
generate_display_tables()
print("Extracting JSON views.")
subprocess.check_call("matUtils extract -i " + pbf + "-K extraction_targets.txt:50 -M cluster_labels.tsv", shell=True)
subprocess.check_call("mv *json display_json/",shell=True)
