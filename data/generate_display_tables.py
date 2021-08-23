filelines = {}
conversion = {"AL":"Alabama","AK":"Alaska","AR":"Arkansas","AZ":"Arizona","CA":"California","CO":"Colorado",
"CT":"Connecticut","DE":"Delaware","DC":"District of Columbia","FL":"Florida","GA":"Georgia","HI":"Hawaii",
"ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine",
"MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana",
"NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina",
"ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island",
"SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia",
"WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming","PR":"Puerto Rico"}

with open("hardcoded_clusters.tsv") as inf:
    for entry in inf:
        spent = entry.strip().split("\t")
        if spent[0] == "cluster_id":
            continue
        #the output clusters table is already sorted by 
        #growth score, so we can use that sorting information
        #to make this substantially easier.
        #just store the first 5 encountered
        #for each unique region encountered.
        reg = conversion[spent[9]]
        if reg not in filelines:
            filelines[reg] = []
        if len(filelines[reg]) < 5:
            #many assumptions that make this faulty if we ever change tree handling.
            #oh well.
            if "node" in spent[0]:
                filelines[reg].append(entry.strip())

header = "Cluster ID,Region,Sample Count,Earliest Date,Latest Date,Clade/Lineage,Inferred Origins,Inferred Origin Confidences"
for reg, lines in filelines.items():
    with open("display_tables/" + reg + "_topclusters.csv", "w+") as outf:
        print(header,file=outf)
        for l in lines:
            #process the line 
            #into something more parseable.
            spent = l.split("\t")
            outline = [spent[0], spent[9], spent[1], spent[2], spent[3], spent[12], spent[10], spent[11]]
            print(",".join(outline),file=outf)