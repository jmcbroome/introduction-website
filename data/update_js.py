#python "backend" code for prepping us-states.js data from a tsv for interactive website display
#it only needs to be ran once per updated tree
#import pandas as pd
import json
import math
import datetime as dt
from dateutil.relativedelta import relativedelta
#cdf = pd.read_csv('hardcoded_clusters.tsv',sep='\t')
def update_js(target, conversion = {}):
    svd = {"type":"FeatureCollection", "features":[]}
    monthswap = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}
    conversion.update({v:v for k,v in conversion.items()})
    conversion["indeterminate"] = "indeterminate"
    #print(conversion)
    #ivc = cdf.region.value_counts()
    datepoints = ["all", dt.date.today()-relativedelta(months=12), dt.date.today()-relativedelta(months=6), dt.date.today()-relativedelta(months=3)]
    #here, the data is stored in a series of dictionaries
    #which are generally structured with the minimum date as the outermost layer
    #then the destination of an introduction
    #than the source of an introduction
    prefd = {datepoints[0]:"", datepoints[1]:"12_", datepoints[2]:"6_", datepoints[3]:"3_"}
    dinvc = {d:{} for d in datepoints}
    dsvc = {d:{} for d in datepoints}
    dotvc = {d:{} for d in datepoints}
    dovc = {d:{} for d in datepoints}
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
                    for tlo in spent[10].split(","):
                        orig = conversion[tlo]
                        if orig not in otvc:
                            otvc[orig] = 0
                        otvc[orig] += 1
                        if orig not in ovc[reg]:
                            ovc[reg][orig] = 0
                        ovc[reg][orig] += 1
    dsumin = {sd:sum(invc.values()) for sd,invc in dinvc.items()}
    sids = {}
    f = open(target)
    geojson_lines = json.load(f)
    f.close()
    id = 0
    #we fill in the basic count of introductions to each area first
    #as well as fill in an integer "ID" if its not already present
    for data in geojson_lines["features"]:
        data["properties"]["intros"] = {}
        for sd, invc in dinvc.items():
            prefix = prefd[sd]
            data["properties"]["intros"][prefix + "basecount"] = invc.get(data["properties"]["name"],0) 
        svd["features"].append(data)
        if "id" in data:
            sids[data["properties"]["name"]] = data["id"]
        else:
            data["id"] = str(id)
            sids[data["properties"]["name"]] = str(id)
            id += 1
    #update the data intros list with specific state values
    for ftd in svd["features"]:
        #update the ftd["properties"]["intros"] with each state
        #state introductions to itself, for now, I will fill with indeterminate
        #this is transposed so that the introductions to each state are stored across each other state by origin
        #in order that coloring and hovertext can be correctly accessed.
        iid = ftd['properties']["name"]
        #for timeslice
        for sd, ovc in dovc.items():
            #get everything where this specific row/region is an origin
            prefix = prefd[sd]
            #fill with 0
            inv_ovc = {k:subd.get(iid,0) for k,subd in ovc.items()}
            print(inv_ovc)
            for destination, count in inv_ovc.items():
                #scale the count for display
                if destination == "indeterminate":
                    continue
                did = sids[conversion.get(destination,destination)]
                ftd["properties"]["intros"][prefix + "raw" + did] = count
                if count > 5:
                    sumin = dsumin[sd]
                    invc = dinvc[sd]
                    otvc = dotvc[sd]
                    ftd["properties"]["intros"][prefix + did] = math.log10(count * sumin / invc[destination] / otvc[iid])
                else:
                    #if there are less than 5 counts, the log correction can do some pretty extreme highlighting
                    #for example, even a single introduction between two distant places may be surprising
                    #but that doesn't mean it should get a lot of emphasis. So we cut off anything with less than 5 introductions total.
                    ftd["properties"]["intros"][prefix + did] = -0.5
    with open("regions.js","w") as outf:
        print("//data updated via update_js.py",file=outf)
        print('var None = "None"',file=outf)
        print('var introData = {"type":"FeatureCollection","features":[',file=outf)
        for propd in svd['features']:
            assert "intros" in propd["properties"]
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
    update_js("us-states.geo.json",stateconv)
