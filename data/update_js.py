#python "backend" code for prepping us-states.js data from a tsv for interactive website display
#it only needs to be ran once per updated tree
#import pandas as pd
import ast
import math
import datetime as dt
from dateutil.relativedelta import relativedelta
#cdf = pd.read_csv('hardcoded_clusters.tsv',sep='\t')
def update_js(target, conversion = {}):
    svd = {"type":"FeatureCollection", "features":[]}
    monthswap = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}
    conversion.update({v:k for k,v in conversion.items()})
    conversion["indeterminate"] = "indeterminate"
    #ivc = cdf.region.value_counts()
    datepoints = ["all", dt.date.today()-relativedelta(months=12), dt.date.today()-relativedelta(months=6), dt.date.today()-relativedelta(months=3)]
    prefd = {datepoints[0]:"", datepoints[1]:"12_", datepoints[2]:"6_", datepoints[3]:"3_"}
    dinvc = {d:{} for d in datepoints}
    dsvc = {d:{} for d in datepoints}
    dotvc = {d:{} for d in datepoints}
    dovc = {d:{k:{} for k in conversion.keys()} for d in datepoints}
    with open("hardcoded_clusters.tsv") as inf:
        for entry in inf:
            spent = entry.strip().split("\t")
            if spent[0] == "cluster_id":
                continue
            reg = conversion[spent[9]]
            if spent[10] == "indeterminate":
                continue
            #get the date of this cluster's earliest sample into a usable form
            dsplt = spent[2].split("-")
            if dsplt == "no-valid-date".split("-"):
                cdate = dt.date(year=2019,month=11,day=1)
            else:
                cdate = dt.date(year=int(dsplt[0]), month=int(monthswap[dsplt[1]]), day=int(dsplt[2]))
            for startdate, ovc in dovc.items():
                if startdate == "all" or cdate > startdate:
                    if reg not in dsvc[startdate]:
                        dsvc[startdate][reg] = 0
                    dsvc[startdate][reg] += spent[-1].count(',') + 1
                    if reg not in dinvc[startdate]:
                        dinvc[startdate][reg] = 0
                    dinvc[startdate][reg] += 1
                    otvc = dotvc[startdate]
                    ovc = dovc[startdate]
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
    dsumin = {sd:sum(invc.values()) for sd,invc in dinvc.items()}

    #print(invc.keys())
    sids = {}
    with open(target) as inf:
        for entry in inf:
            if entry[0:2] == "//" or entry[0:3] == "var" or entry[0] == "]":
                continue
            data = ast.literal_eval(entry.strip().strip(","))
            data["properties"]["intros"] = {}
            for sd, invc in dinvc.items():
                prefix = prefd[sd]
                data["properties"]["intros"][prefix + "basecount"] = invc.get(data["properties"]["name"],0) 
            svd["features"].append(data)
            sids[data["properties"]["name"]] = data["id"]
    #update the data intros list with specific state values
    for ftd in svd["features"]:
        #update the ftd["properties"]["intros"] with each state
        #state introductions to itself, for now, I will fill with indeterminate
        iid = ftd['properties']["name"]
        for sd, ovc in dovc.items():
            prefix = prefd[sd]
            for origin, count in ovc[iid].items():
                #scale the count for display
                if origin in sids:
                    oid = sids[origin]
                else:
                    oid = sids[iid]
                ftd["properties"]["intros"][prefix + "raw" + oid] = count
                if count > 5:
                    sumin = dsumin[sd]
                    invc = dinvc[sd]
                    otvc = dotvc[sd]
                    ftd["properties"]["intros"][prefix + oid] = math.log10(count * sumin / invc[iid] / otvc[origin])
                else:
                    ftd["properties"]["intros"][prefix + oid] = -0.5
    with open(target,"w") as outf:
        print("//data updated via updated-us-states.py",file=outf)
        print('var introStatesData = {"type":"FeatureCollection","features":[',file=outf)
        for propd in svd['features']:
            print(str(propd) + ",",file=outf)
        print("]};",file=outf)
stateconv = {"AL":"Alabama","AK":"Alaska","AR":"Arkansas","AZ":"Arizona","CA":"California","CO":"Colorado",
    "CT":"Connecticut","DE":"Delaware","DC":"District of Columbia","FL":"Florida","GA":"Georgia","HI":"Hawaii",
    "ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine",
    "MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana",
    "NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina",
    "ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island",
    "SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia",
    "WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming","PR":"Puerto Rico"}
if __name__ == "__main__":
    update_js("us-states.js",stateconv)