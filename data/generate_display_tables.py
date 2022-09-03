import json, gzip

def generate_display_tables():
    #function to convert date format from YYYY-Mon-DD to YYYY-MM-DD
    def fix_month(datestr):
        monthswap = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}
        splitr = datestr.split("-")
        return splitr[0] + "-" + monthswap.get(splitr[1],splitr[1]) + "-" + splitr[2]
    # function to add quotes around a variable for JSON formatting
    def addq(item):
        return "\"" + item + "\""

    # get clusters data and put into array
    cluster_data = []
    bad_date_data = []
    with open("hardcoded_clusters.tsv") as inf:
        for entry in inf:
            spent = entry.strip().split("\t")
            if spent[0] == "cluster_id": 
                continue
            if spent[2] == "no-valid-date" and spent[3] == "no-valid-date":
                bad_date_data.append(spent)
            else:
                #fix date format
                spent[2] = fix_month(spent[2])
                spent[3] = fix_month(spent[3])
                cluster_data.append(spent)
    
    #now, sort by growth score
    cluster_data.sort(key = lambda x: x[4], reverse = True)
    # sort clusters with no-valid-date by growth score and append to cluster_data at the end
    bad_date_data.sort(key = lambda x: x[4], reverse = True)
    cluster_data.extend(bad_date_data)

    #output data to be compatible with parse.JSON
    # -create as compact a string as possible,
    # -only add quotes to items that are strings to save space
    txt_data = "["
    txt_samples = "["
    for i, d in enumerate(cluster_data):
        outline_data = [addq(d[0]), addq(d[9]), d[1], addq(d[2]), addq(d[3]), addq(d[12]), addq(d[13]), addq(d[10]), d[11], d[4]]
        outline_samples = [addq(d[15])]
        txt_data += "[" + ",".join(outline_data) + "]"
        txt_samples += "[" + ",".join(outline_samples) + "]"
        if i == len(cluster_data)-1:
            txt_data += "]"
            txt_samples += "]"
        else:
            txt_data += ","
            txt_samples += ","
       
    #now write data to file, and gzip for quicker loading into browser
    #basic cluster data (no samples) 
    with gzip.open("cluster_data.json.gz", "wb") as f:
        f.write(txt_data.encode())
    #sample names for each cluster
    with gzip.open("sample_data.json.gz", "wb") as f:
        f.write(txt_samples.encode())

if __name__ == "__main__":
    generate_display_tables()
