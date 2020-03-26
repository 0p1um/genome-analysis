Simple project to do deeper analysis of raw 23 and me genome file.
The scripts uses python3.

It gather open source data about your snps and write it in a json file called `snp_analysis.json`.

```
./get_snp_data.py <path_to_your_genome_file>
```

To read data in the json file in your cli do:
```
./format_snps_analysis.py snp_analysis.json
```
