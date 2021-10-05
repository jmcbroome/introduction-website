def generate_display_tables(conversion = {}, host = "https://raw.githubusercontent.com/jmcbroome/introduction-website/main/"):
    filelines = {}
    def fix_month(datestr):
        monthswap = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}
        splitr = datestr.split("-")
        return splitr[0] + "-" + monthswap.get(splitr[1],splitr[1]) + "-" + splitr[2]
    default_growthvs = []
    default_lines = []
    with open("hardcoded_clusters.tsv") as inf:
        for entry in inf:
            spent = entry.strip().split("\t")
            if spent[0] == "cluster_id" or spent[3] == "no-valid-date":
                continue
            #new method- we just store all of them and use paging
            #split each file by state
            # reg = conversion[spent[9]]
            # if reg not in filelines:
            #     filelines[reg] = []  
            # filelines[reg].append(entry.strip())
            # default_lines[float(spent[4])] = entry.strip()
            #the output clusters table is already sorted by 
            #growth score, so we can use that sorting information
            #to make this substantially easier.
            #just store the first 5 encountered
            #for each unique region encountered.
            reg = conversion[spent[9]]
            if reg not in filelines:
                filelines[reg] = []
            if len(filelines[reg]) < 100:
                filelines[reg].append(entry.strip())
            #now, check to see if this scores in the top 100 overall. Significantly more complicated since we have to sort things out as we go here.
            if len(default_lines) < 100:
                default_growthvs.append(float(spent[4]))
                default_lines.append(entry.strip())
            elif float(spent[4]) > min(default_growthvs):
                popind = default_growthvs.index(min(default_growthvs))
                default_growthvs.pop(popind)
                default_lines.pop(popind)
                default_growthvs.append(float(spent[4]))
                default_lines.append(entry.strip())
                assert len(default_lines) == 100

    header = "Cluster ID\tRegion\tSample Count\tEarliest Date\tLatest Date\tClade\tLineage\tInferred Origins\tInferred Origin Confidences\tGrowth Score\tClick to View"
    mout = open("cluster_labels.tsv","w+")
    print("sample\tcluster",file=mout)
    for reg, lines in filelines.items():
        with open("display_tables/" + conversion[reg] + "_topclusters.tsv", "w+") as outf:
            print(header,file=outf)
            for l in lines:
                #process the line 
                #into something more parseable.
                spent = l.split("\t")
                #save matching results to the other output files
                #for downstream extraction of json
                samples = spent[-1].split(",")
                for s in samples:
                    print(s + "\t" + spent[0],file=mout)
                #generate a link to exist in the last column
                #based on the global "host" variable.
                #and including all html syntax.
                link = "https://cov2tree-git-newnewmeta-theosanderson.vercel.app/?protoUrl=" + host + "data/cview.pb.gz"
                link += '&search=[{"id":0.123,"category":"cluster","value":"'
                link += spent[0]
                link += '","enabled":true,"aa_final":"any","min_tips":1,"aa_gene":"S","search_for_ids":""}]'
                link += '&colourBy={"variable":"region","gene":"S","colourLines":false,"residue":"681"}'
                link += "&zoomToSearch=0"
                #additionally process the date strings
                outline = [spent[0], spent[9], spent[1], fix_month(spent[2]), fix_month(spent[3]), spent[12], spent[13], spent[10], spent[11], spent[4], link]
                print("\t".join(outline),file=outf)

    mout.close()
    sorted_defaults = sorted(list(zip(default_growthvs,default_lines)),key=lambda x:-x[0])
    with open("display_tables/default_clusters.tsv","w+") as outf:
        print(header,file=outf)
        for gv,dl in sorted_defaults:
            spent = dl.split("\t")
            link = "https://cov2tree-git-newnewmeta-theosanderson.vercel.app/?protoUrl=" + host + "data/cview.pb.gz"
            link += '&search=[{"id":0.123,"category":"cluster","value":"'
            link += spent[0]
            link += '","enabled":true,"aa_final":"any","min_tips":1,"aa_gene":"S","search_for_ids":""}]'
            link += '&colourBy={"variable":"region","gene":"S","colourLines":false,"residue":"681"}'
            link += "&zoomToSearch=0"
            outline = [spent[0], spent[9], spent[1], fix_month(spent[2]), fix_month(spent[3]), spent[12], spent[13], spent[10], spent[11], spent[4], link]
            print("\t".join(outline), file = outf)
stateconv = {"AL":"Alabama","AK":"Alaska","AR":"Arkansas","AZ":"Arizona","CA":"California","CO":"Colorado",
    "CT":"Connecticut","DE":"Delaware","DC":"District of Columbia","FL":"Florida","GA":"Georgia","HI":"Hawaii",
    "ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine",
    "MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana",
    "NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina",
    "ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island",
    "SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia",
    "WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming","PR":"Puerto Rico"}
stateconv.update({v:v for v in stateconv.values()})
if __name__ == "__main__":
    generate_display_tables(stateconv, host = "https://raw.githubusercontent.com/jmcbroome/introduction-website/main/")
