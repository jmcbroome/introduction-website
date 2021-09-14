import subprocess
from master_backend import primary_pipeline, read_lexicon, parse_setup
#This script is a wrapper around the primary pipeline script
#which does all necessary preprocessing to generate the setup for a united states analysis.
args = parse_setup()
conversion = read_lexicon(args.lexicon)
pbf = args.input
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
#update the arguments parsed
args.input = "clean.pb"
args.sample_regions = "sample_regions.tsv"
args.geojson = "us-states.geo.json"
print("Starting main pipeline.")
primary_pipeline(args)