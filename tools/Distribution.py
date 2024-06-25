import sys
import os
import pyasn
import pandas as pd
import numpy as np
import pytricia
from iso3166 import countries

sys.path.append(os.getcwd())
from tools.APD import iplisttrans

asndb = pyasn.pyasn('./tools/data/ipasn_20221212.dat')

def AS_statistics(file):
    ASname_dict = dict()
    data = pd.read_csv('./analysis/data/GeoLite2-ASN-Blocks-IPv6.csv')
    for _, line in data.iterrows():
        ASname_dict[line["autonomous_system_number"]] = line["autonomous_system_organization"]

    asn_data = {}
    asn_data_top = {}

    with open(file) as f:
        lines = f.read().splitlines()
        asn_data["Unknown"] = 0
        for line in lines:
            ip = line.split(',', 1)[0] 
            asn, prefix = asndb.lookup(ip)
            if not asn:
                asn_data["Unknown"] += 1  
                continue
            if "AS" + str(asn) not in asn_data.keys():
                asn_data["AS" + str(asn)] = 0
            asn_data["AS" + str(asn)] += 1

    LS = 0
    for k, v in asn_data.items():
        LS += np.log(v) / np.log(100)

    print("IP Num:", len(lines), "AS Num:", len(asn_data) - 1, 'LS:', round(LS,2))
    asn_data = sorted(asn_data.items(), key=lambda x: x[1], reverse=True)
    asn_data_top = dict([asn_data[i] for i in range(4)])
    asn_data_top["Other"] = len(lines) - sum(asn_data_top.values())
    for k, v in asn_data_top.items():
        if k != 'Other' and k != 'Unknown':
            print(ASname_dict[int(k[2:])], k[2:], round(v/len(lines)*100, 2), '%', v)

def AS_similarity(file_prior, file_later):
    ASname_dict = dict()
    data = pd.read_csv('./tools/data/GeoLite2-ASN-Blocks-IPv6.csv')
    for _, line in data.iterrows():
        ASname_dict[line["autonomous_system_number"]] = line["autonomous_system_organization"]
    asn_data_prior = {}
    with open(file_prior) as f:
        lines = f.read().splitlines()
        asn_data_prior["Unknown"] = set()
        for line in lines:
            ip = line.split(',', 1)[0] 
            asn, prefix = asndb.lookup(ip)
            if not asn:
                asn_data_prior["Unknown"].add(ip)  
                continue
            if "AS" + str(asn) not in asn_data_prior.keys():
                asn_data_prior["AS" + str(asn)] = set()
            asn_data_prior["AS" + str(asn)].add(ip)
    
    asn_data_later = {}
    with open(file_later) as f:
        lines = f.read().splitlines()
        asn_data_later["Unknown"] = set()
        for line in lines:
            ip = line.split(',', 1)[0] 
            asn, prefix = asndb.lookup(ip)
            if not asn:
                asn_data_later["Unknown"].add(ip)  
                continue
            if "AS" + str(asn) not in asn_data_later.keys():
                asn_data_later["AS" + str(asn)] = set()
            asn_data_later["AS" + str(asn)].add(ip)

    asn_similarity = dict()
    for k in asn_data_prior.keys():
        if k in asn_data_later.keys():
            jaccard_distance = 1 - (len(asn_data_prior[k] & asn_data_later[k]) / len(asn_data_prior[k] | asn_data_later[k]))
            size_index = np.log10(len(asn_data_prior[k] ^ asn_data_later[k]) + 1)
            asn_similarity[k] = jaccard_distance * size_index

    asn_similarity_top = dict()
    asn_similarity_re = dict()
    asn_similarity = sorted(asn_similarity.items(), key=lambda x: x[1], reverse=True)
    asn_similarity_top = dict([asn_similarity[i] for i in range(11)])
    for k, v in asn_similarity_top.items():
        if k != "Unknown":
            print(ASname_dict[int(k[2:])], k[2:], "Scan inconsistency:", v)
            asn_similarity_re[k] = asn_data_prior[k] ^ asn_data_later[k]
    return asn_similarity_re

def CC_statistics(file_name):
    data = pd.read_csv('./tools/data/RIPE-Country-IPv6.csv')
    pyt = pytricia.PyTricia(128)
    for _, line in data.iterrows():
        if line["prefixes"] != "prefixes":
            pyt.insert(line["prefixes"], line["country code"])            

    unknow_list = list()
    geo_data = {}
    with open(file_name) as f:
        lines = f.read().splitlines()
        for line in lines:
            ip = line.split(',', 1)[0] 
            geo = pyt.get(ip)
            if not geo:
                unknow_list.append(ip)  
                continue
            if geo not in geo_data.keys():
                geo_data[geo] = 0
            geo_data[geo] += 1

    LS = 0
    for k, v in cc_data.items():
        LS += np.log(v) / np.log(100)  

    total = len(lines)
    print("Total IPs:", total, "Total country:", len(cc_data), "LS:", round(LS, 2))
    cc_data = sorted(cc_data.items(), key=lambda x: x[1], reverse=True)
    cc_data_top = dict([cc_data[i] for i in range(4)])
    for k, v in cc_data_top.items():
        print(countries.get(k).name, k, round(v/total*100,2), '%')

def Prefix_statistics(file_name, lens):    
    lines = open(file_name).readlines()
    lines = [line.split(',', 1)[0] for line in lines]
    lines = iplisttrans(lines)  
    lens = int(lens/4)
    ip_dict = dict()
    for line in lines:
        k = line[:lens]
        if k in ip_dict.keys():
            ip_dict[k] += 1
        else:
            ip_dict[k] = 1

    LS = 0
    for k, v in ip_dict.items():
        LS += np.log(v) / np.log(1000)
    total = sum(ip_dict.values())
    print("Total IPs:", total, "Total /", lens*4, "prefixes:", len(ip_dict.keys()), "LS:", round(LS, 2))
    ip_dict = sorted(ip_dict.items(), key=lambda x: x[1], reverse=True)
    ip_dict_top = dict([ip_dict[i] for i in range(4)])
    for k, v in ip_dict_top.items():
        print(k, round(v/total * 100, 2), '%')

if __name__ == "__main__":
    pass