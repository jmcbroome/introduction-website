def generate_display_tables():
    filelines = {}
    conversion = {"AL":"Alabama","AK":"Alaska","AR":"Arkansas","AZ":"Arizona","CA":"California","CO":"Colorado",
    "CT":"Connecticut","DE":"Delaware","DC":"District of Columbia","FL":"Florida","GA":"Georgia","HI":"Hawaii",
    "ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine",
    "MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana",
    "NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina",
    "ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island",
    "SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia",
    "WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming","PR":"Puerto Rico"}
    #this will need to be edited on migrating to a proper host service.
    host = "https://raw.githubusercontent.com/jmcbroome/introduction-website/main/"

    default_lines = {}
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
            #now, check to see if this scores in the top five overall.
            if len(default_lines) < 100:
                default_lines[float(spent[4])] = entry.strip()
            elif float(spent[4]) > max(default_lines.keys()):
                default_lines.pop(min(default_lines.keys()))
                default_lines[float(spent[4])] = entry.strip()
                assert len(default_lines) == 100

    header = "Cluster ID\tRegion\tSample Count\tEarliest Date\tLatest Date\tClade/Lineage\tInferred Origins\tInferred Origin Confidences\tGrowth Score\tClick to View"
    mout = open("cluster_labels.tsv","w+")
    print("sample\tcluster",file=mout)
    for reg, lines in filelines.items():
        with open("display_tables/" + reg + "_topclusters.tsv", "w+") as outf:
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
                link = "https://cov2tree.org/?protoUrl=" + host + "data/cview.pb"
                link += '&search=[{"id":0.123,"category":"country","value":"'
                link += "USA_" + spent[0]
                link += '","enabled":true,"aa_final":"any","min_tips":1,"aa_gene":"S","search_for_ids":""}]'
                link += '&colourBy={"variable":"none","gene":"S","colourLines":false,"residue":"681"}'
                outline = [spent[0], spent[9], spent[1], spent[2], spent[3], spent[12], spent[10], spent[11], spent[4], link]
                print("\t".join(outline),file=outf)

    mout.close()
    sorted_default_keys = sorted(list(default_lines.keys()),reverse=True)
    with open("display_tables/default_clusters.tsv","w+") as outf:
        print(header,file=outf)
        for k in sorted_default_keys:
            spent = default_lines[k].split("\t")
            link = "https://cov2tree.org/?protoUrl=" + host + "data/cview.pb"
            link += '&search=[{"id":0.123,"category":"country","value":"'
            link += "USA_" + spent[0]
            link += '","enabled":true,"aa_final":"any","min_tips":1,"aa_gene":"S","search_for_ids":""}]'
            link += '&colourBy={"variable":"none","gene":"S","colourLines":false,"residue":"681"}'
            outline = [spent[0], spent[9], spent[1], spent[2], spent[3], spent[12], spent[10], spent[11], spent[4], link]
            print("\t".join(outline), file = outf)
#generate_display_tables()