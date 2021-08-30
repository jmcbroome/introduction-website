#python "backend" code for prepping us-states.js data from a tsv for interactive website display
#it only needs to be ran once per updated tree
#import pandas as pd
import ast
import math
#cdf = pd.read_csv('hardcoded_clusters.tsv',sep='\t')
def update_us_states():
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
    conversion["indeterminate"] = "indeterminate"
    #ivc = cdf.region.value_counts()
    invc = {}
    svc = {}
    otvc = {}
    ovc = {k:{} for k in conversion.keys()}
    with open("hardcoded_clusters.tsv") as inf:
        for entry in inf:
            spent = entry.strip().split("\t")
            if spent[0] == "cluster_id":
                continue
            reg = conversion[spent[9]]
            if spent[10] == "indeterminate":
                continue
            #reg = spent[9]
            if reg not in svc:
                svc[reg] = 0
            svc[reg] += spent[-1].count(',') + 1
            if reg not in invc:
                invc[reg] = 0
            invc[reg] += 1
            if reg not in ovc:
                ovc[reg] = {}
            confidence = [float(c) for c in spent[11].split(",")]
            for i,tlo in enumerate(spent[10].split(",")):
                if confidence[i] < 0.1:
                    continue
                orig = conversion[tlo]
                if orig not in otvc:
                    otvc[orig] = 0
                otvc[orig] += 1
                if orig not in ovc[reg]:
                    ovc[reg][orig] = 0
                ovc[reg][orig] += 1
    sumin = sum(invc.values())

    #print(invc.keys())
    sids = {}
    with open("us-states.js") as inf:
        for entry in inf:
            if entry[0:2] == "//" or entry[0:3] == "var" or entry[0] == "]":
                continue
            data = ast.literal_eval(entry.strip().strip(","))
            data["properties"]["intros"] = {}
            data["properties"]["intros"]["basecount"] = invc.get(data["properties"]["name"],0) #/ svc[data["properties"]["name"]]
            svd["features"].append(data)
            sids[data["properties"]["name"]] = data["id"]
    #update the data intros list with specific state values
    for ftd in svd["features"]:
        #update the ftd["properties"]["intros"] with each state
        #state introductions to itself, for now, I will fill with indeterminate
        iid = ftd['properties']["name"]
        for origin, count in ovc[iid].items():
            #scale the count for display
            if origin in sids:
                oid = sids[origin]
            else:
                oid = sids[iid]
            ftd["properties"]["intros"]["raw" + oid] = count
            if count > 5:
                ftd["properties"]["intros"][oid] = math.log10(count * sumin / invc[iid] / otvc[origin])
            else:
                ftd["properties"]["intros"][oid] = -0.5
    with open("us-states.js","w") as outf:
        print("//data updated via updated-us-states.py",file=outf)
        print('var introStatesData = {"type":"FeatureCollection","features":[',file=outf)
        for propd in svd['features']:
            print(str(propd) + ",",file=outf)
        print("]};",file=outf)
#update_us_states()