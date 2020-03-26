#!/usr/bin/python3
import json
import sys


if len(sys.argv) <= 1:
    print('Please give file as argument.')
    sys.exit(0)

data_file = sys.argv[1]

with open(data_file) as f:
    data=json.load(f)

data_to_print={}

#keep only snps with analysis data
for e in data:
    if 'snpedia_result' in e:
        rsid = e['rsid']
        genotype = e['genotype']
        # match result with actual genotype
        for result in e['snpedia_result']:
            if genotype == result['geno']:
                summary = result['summary']
                url = result['url']
        if summary in data_to_print:
            data_to_print[summary]['snps'].append({'rsid':rsid,'genotype':genotype,'url':url})
        else:
            data_to_print[summary]={'snps':[{'rsid':rsid,'genotype':genotype,'url':url}]}

for key, item in data_to_print.items():
    print(key)
    for snp in item['snps']:
        print('%s\t%s\t%s' % (snp['rsid'], snp['genotype'], snp['url']))
    print('---------------\n')

