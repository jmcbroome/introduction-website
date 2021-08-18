#python "backend" code for prepping us-states.js data from a tsv for interactive website display
#it only needs to be ran once per updated tree
#import pandas as pd
import ast
#cdf = pd.read_csv('hardcoded_clusters.tsv',sep='\t')
svd = {"type":"FeatureCollection", "features":[]}
conversion = {"AL":"Alabama","AK":"Alaska","AR":"Arkansas","AZ":"Arizona","CA":"California","CO":"Colorado",
"CT":"Connecticut","DE":"Delaware","DC":"District of Columbia","FL":"Florida","GA":"Georgia","HI":"Hawaii",
"ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine",
"MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana",
"NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina",
"ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island",
"SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia",
"WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming","PR":"Puerto Rico"}
conversion.update({v:k for k,v in conversion.items()})
#ivc = cdf.region.value_counts()
ivc = {}
with open("hardcoded_clusters.tsv") as inf:
    for entry in inf:
        spent = entry.strip().split("\t")
        if spent[0] == "cluster_id":
            continue
        reg = conversion[spent[9]]
        if reg not in ivc:
            ivc[reg] = 0
        ivc[reg] += 1
#print(ivc.keys())
with open("us-states.js") as inf:
    for entry in inf:
        if entry[0:2] == "//" or entry[0:3] == "var" or entry[0] == "]":
            continue
        #print(entry.strip())
        data = ast.literal_eval(entry.strip().strip(","))
        print(data)
        data["properties"]["intros"] = ivc[data["properties"]["name"]]
        svd["features"].append(data)
with open("us-states.js","a") as outf:
    print("//data updated via updated-us-states.py",file=outf)
    print('var introStatesData = {"type":"FeatureCollection","features":[',file=outf)
    for propd in svd['features']:
        print(str(propd) + ",",file=outf)
    print("]};",file=outf)