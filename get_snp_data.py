#!/usr/bin/python3
import sys
from lxml import html
from time import sleep
import requests
import json


if len(sys.argv) <= 1:
    print('Please give file as argument.')
    sys.exit(0)

data_file = sys.argv[1]
results = []


def get_snpedia_data(rsid):
    """Function that gets data from snpedia using a SNPs id"""

    snpedia_baseurl = 'http://snpedia.com/index.php/'

    print('Get data for rsid: '+rsid)

    # if request for data failed, wait and request the data again
    while 1:
        try:
            raw_response = requests.get(snpedia_baseurl+rsid)
            break
        except:
            print('Request for data failed, wait 60 seconds to request again ...')
            sleep(60)
            continue

    html_response=html.fromstring(raw_response.content)

    try:
        # get the StabilizedOrientation
        orientation = html_response.xpath('/html/body/div[1]/div[6]/div/div/div[3]/div[1]/div/div[1]/table[2]/tbody/tr/td[2]/text()')[0]
        # get all the possible variations data for this snp
        snpedia_genotypes = [{'geno':e.xpath('./td[1]/a/text()')[0].replace('(','').replace(')','').split(';'), 'url':'https://snpedia.org'+e.xpath('./td[1]/a/@href')[0],'summary':e.xpath('./td[3]/text()')[0]} for e in html_response.xpath('/html/body/div[1]/div[6]/div/div/div[3]/div[1]/div/div[1]/table[3]/tbody/tr')[1:]]
        print(snpedia_genotypes)
        
        # if the StabilizedOrientation is minus, the snp variation need to be changed to be matched with 23 and me data
        # we substitue nucleotides with their matching ones and we take the reversed result because it is read from dna bottom to top
        if orientation == 'minus':
            subs = { "A": "T",
                    "T": "A",
                    "C": "G",
                    "G": "C" }
            for index, element in enumerate(snpedia_genotypes):
                snpedia_genotypes[index]['geno'] = ''.join(map(subs.get, element['geno']))[::-1]
        # else the StabilizedOrientation is the same than in 23 and me data so we keep the snp variation as it is
        else:
            for index, element in enumerate(snpedia_genotypes):
                snpedia_genotypes[index]['geno'] = ''.join(element['geno'])
    except:
        print('Failed to get data for '+rsid)
        return []



    return snpedia_genotypes

def list_snpedia_snps():
    """List all snps registered in snpedia"""

    cmcontinue = ''
    batch = requests.get('https://bots.snpedia.com/api.php?format=json&action=query&list=categorymembers&cmtitle=Category:Is_a_snp&cmlimit=500'+cmcontinue)
    batch = json.loads(batch.text)
    list_of_snps = [e['title'] for e in batch['query']['categorymembers']]

    while 'continue' in batch:
        cmcontinue='&cmcontinue='+batch['continue']['cmcontinue']
        c = batch['continue']['continue']
        batch = requests.get('https://bots.snpedia.com/api.php?format=json&action=query&list=categorymembers&cmtitle=Category:Is_a_snp&cmlimit=500'+cmcontinue)
        batch = json.loads(batch.text)
        # add the title of snps pages in that batch to the list
        list_of_snps.extend([e['title'].lower() for e in batch['query']['categorymembers']])
        print(len(list_of_snps))
    return list_of_snps

with open(data_file) as f:
    for l in f:
        if l[0:1] == '#':
            continue
        else:
            l=l.replace('\n','')
            l=l.split('\t')
            results.append({'rsid':l[0], 'chromosome':l[1], 'position':l[2], 'genotype':l[3]})

print(get_snpedia_data('rs4988235'))
print(get_snpedia_data('rs3131972'))
print(len(results))
print('Getting list of snps registered in snpedia ...')
list_of_snps = list_snpedia_snps()
print(list_of_snps)

for index, element in enumerate(results):
    rsid = element['rsid']
    if rsid in list_of_snps:
        snpedia_genotypes = get_snpedia_data(element['rsid'])
        print(snpedia_genotypes)
        if snpedia_genotypes != []:
            for variation in snpedia_genotypes:
                if variation['geno'] == element['genotype']:
                    results[index]['snpedia_result'] = snpedia_genotypes

with open('snps_analysis.json', 'w') as f:
    json.dump(results, f)
