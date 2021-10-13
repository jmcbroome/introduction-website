# introduction-website
Code to generate a webpage displaying introductions inferred via [matUtils introduce](https://usher-wiki.readthedocs.io/en/latest/matUtils.html#introduce). Contains additional scripts and files required to generate a map for each state of the United States. To construct a site for a different region, additional files and preprocessing is required.

## Quickstart: Display the United States

This site uses python to perform backend setup and vanilla javascript for website rendering. You will need to have the [UShER software suite](https://usher-wiki.readthedocs.io/en/latest/Installation.html) installed and available on your path. Some versions of python may be missing the dateutil standard package as well, which is a required dependency; it can be installed via conda.

Clone this repository into your workspace of choice, then obtain the [latest public data from the MAT repository](http://hgdownload.soe.ucsc.edu/goldenPath/wuhCor1/UShER_SARS-CoV-2/)- specifically, "public-latest.all.masked.pb" and "public-latest.metadata.tsv.gz". Unzip the metadata file with your preferred tool. Additionally download the [gtf](https://usher-wiki.readthedocs.io/en/latest/_downloads/2052d9a7147253e32a3420939550ac63/ncbiGenes.gtf) and [reference](https://raw.githubusercontent.com/yatisht/usher/5e83b71829dbe54a37af845fd23d473a8f67b839/test/NC_045512v2.fa) files to produce a taxodium view. 

Navigate to the "data" directory and run "prepare_us_states.py" with the files obtained above, ala the below.

```
cd data
python3 prepare_us_states.py -i path/to/public-latest.all.masked.pb -m path/to/public-latest.metadata.tsv -H web/accessible/link/to/index/directory -f path/to/NC_045512v2.fa -a path/to/ncbiGenes.gtf -l state_lexicon.txt
gzip cview.pb
```

You can then view your results with a Python server initiated in the main directory.

```
cd ..
python3 -m http.server
```

## The Pipeline and More Explanation

To generate a website for your set of regions of interest, [you will first need to obtain a geojson representing your regions of interest.](https://geojson-maps.ash.ms). You will need to generate a sample-region two-column tsv, with sample identifiers in the first column and the ID of the region they are from in the second column. You will need what I'm calling a "lexicon" file to ensure compatibility between names- this is an unheaded csv containing in the first column the base name of each region to be used by the map, and comma separated after that, each other name for that region across your other files. 

Once you've obtained these files, you can navigate to the data directory and run

```
python3 master_backend.py -i path/to/your.pb -m path/to/matching/metadata.tsv -f path/to/NC_045512v2.fa -a path/to/ncbiGenes.gtf -j path/to/your/geo.json -s path/to/your/sample_regions.tsv -l path/to/your/lexicon.txt -H web/accessible/link/to/index/directory
gzip cview.pb
```

You can optionally pass -G or -X parameters, which will be applied when introduce is called. 

Then navigate to the outermost index directory and run 
```
python3 -m http.server
```

It is not required to make the website on a web-accessible directory, but the taxodium view (clicking view cluster on the site) will not function if it's not. You can work around this by uploading the cview.pb / cluster_taxodium.pb that is output by the pipeline directly to [taxodium](https://cov2tree.org/), then search for your cluster of interest from the website table using the search box on the resulting display. 
