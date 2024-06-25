import os
import sys
import re
from datetime import datetime
import ipaddress
import pandas as pd
import pytricia
import pyasn
import json
import zipfile
import shutil

sys.path.append(os.getcwd())
from tools.APD import APM, APD, alias_unfile

def download():
    command = f"hmap -D hitlist"
    os.system(command)
    command = f"hmap -D aliasPrefix"
    os.system(command)
    command = f"mv G* data/"
    os.system(command)

def get_latest_file_with_date(pattern, directory):
    regex = re.compile(rf'{re.escape(pattern)}_(\d{{4}}-\d{{2}}-\d{{2}})')
    latest_date = None
    latest_file = None

    for filename in os.listdir(directory):

        match = regex.search(filename)
        if match:
            file_date = match.group(1)
            file_date = datetime.strptime(file_date, '%Y-%m-%d')
            
            if latest_date is None or file_date > latest_date:
                latest_date = file_date
                latest_file = filename

    return latest_file

def get_Hhitlist_low(Galias):
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    outf = f"data/Hhitlist-low_{date_string}"
    command = f"hmap -w data/prefixes32 -U low -x 42 -b {Galias} -f \"outersaddr\" " \
        f"-o {outf} -O csv -R 200000 --output-filter=\"type=1||type=3||type=129\""
    os.system(command)

def organize_seeds(Gseeds, Hhitlist_low):
    unique_seed = set()

    with open(Gseeds, 'r') as Gf:
        for line in Gf:
            unique_seed.add(line.strip())

    with open(Hhitlist_low, 'r') as Hf:
        for line in Hf:
            unique_seed.add(line.strip())

    print(f"total {len(unique_seed)} seed addresses")
    
    max_seeds_per_file = 10000000
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    seed_count = 0
    file_count = 0
    seed_file = None
    file_list = list()
    Hseeds_path = f'data/Hseeds_{date_string}'
    Hseeds_file = open(Hseeds_path, 'w')

    for line in sorted(unique_seed):
        if seed_count % max_seeds_per_file == 0:
            if seed_file:
                seed_file.close()
            seed_file_path = f'data/Seeds{file_count}_{date_string}'
            seed_file = open(seed_file_path, 'w')
            file_count += 1
            file_list.append(seed_file_path)
            
        seed_file.write(line + '\n')
        seed_count += 1
        Hseeds_file.write(line + '\n')

    if seed_file:
        seed_file.close()
    Hseeds_file.close()
    return file_list

def TGA(seeds, GaliasPrefix):
    outf = seeds.replace("Seeds", "TGA")
    command = f"hmap -I {seeds} -U tga -b {GaliasPrefix} -R 200000 -O csv -o {outf} -f \"outersaddr, type\" " \
        f"--output-filter=\"type=1||type=3||type=129\" --ignore-filelist-error"
    os.system(command)

def get_files_with_tga_prefix(directory):
    pattern = re.compile(r'^TGA\d+')
    matched_files = []
    for filename in os.listdir(directory):
        if pattern.match(filename):
            matched_files.append(filename)
    return matched_files

def loop_remove_alias(filename, aliasfile):
    newfile = APM(filename, aliasfile)
    while(APD(newfile)):
        directory = 'data/'
        HaliasPrefix = directory + get_latest_file_with_date('HaliasPrefix', directory)
        APM(newfile, HaliasPrefix)

def yarrp_trace(targets):
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    command = f"yarrp -t ICMP6 -i {targets} -r 200 -I eno1 -v -o data/Hhitlist-trace_{date_string}"
    os.system(command)    

def merge_results():
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    command = f"cat data/TGA-APD* | sort | uniq > data/Hhitlist-tga_{date_string}"
    os.system(command)
    command = f"rm data/TGA*"
    os.system(command)
    command = f"rm data/Seeds*"
    os.system(command)
    tga = get_latest_file_with_date("Hhitlist-tga", "data")
    trace = get_latest_file_with_date("Hhitlist-trace", "data")
    command = f"cat data/{trace} data/{tga} | sort | uniq > data/Hhitlist_{date_string}"
    os.system(command)

def is_global_ipv6_address(ipv6_address: str) -> bool:
    try:
        # 创建一个 IPv6 地址对象
        ip = ipaddress.IPv6Address(ipv6_address)
        # 判断是否是全局单播地址
        return ip.is_global
    except ipaddress.AddressValueError:
        # 如果地址无效，则返回 False
        return False
    
def rm_invalid_IP(filename):
    ips = list()
    lines = open(filename).readlines()
    for line in lines:
        ip = line.split(',', 1)[0]
        if is_global_ipv6_address(ip):
            ips.append(line)
    print("valid IP number:", len(ips))
    f = open(filename, "w")
    f.writelines(ips)
    f.close() 
    return round(len(ips)/1000000, 2)

def RIPE_geoid():
    data = pd.read_csv('./tools/data/RIPE-Country-IPv6.csv')
    pyt = pytricia.PyTricia(128)
    for _, line in data.iterrows():
        if line["prefixes"] != "prefixes":
            pyt.insert(line["prefixes"], line["country code"])  
    return pyt

def distribution_analysis(file_name):
    asn_dict = dict()
    pyt = RIPE_geoid() # IP to CC
    with open('./tools/data/CC-Country.json', 'r', encoding='utf-8') as f: # CC to country name
        countries_dict = json.load(f)
        cc_dict = {key: [] for key in countries_dict.keys()}

    asndb = pyasn.pyasn('./tools/data/ipasn_20221212.dat') # IP to ASN
    ASname_dict = dict()
    data = pd.read_csv('./tools/data/GeoLite2-ASN-Blocks-IPv6.csv')
    for _, line in data.iterrows():
        ASname_dict[line["autonomous_system_number"]] = line["autonomous_system_organization"]

    with open(file_name) as f:
        lines = f.read().splitlines()
        for line in lines:
            ip = line.split(',', 1)[0] 
            geo = pyt.get(ip)
            if geo in cc_dict.keys():
                cc_dict[geo].append(ip)
            else:
                cc_dict[geo] = [ip]

            asn, prefix = asndb.lookup(ip)
            if asn:
                if asn in asn_dict.keys():
                    asn_dict[asn].append(ip)
                else:
                    asn_dict[asn] = [ip]
  
    # Output top 10 CC information
    top_cc_result = {"data": [], "unit": "M"}
    print('Total CC:', len(cc_dict))
    top10_cc = sorted(cc_dict.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for cc, ips in top10_cc: 
        top_cc_result["data"].append({"name": f"{cc}-{countries_dict[cc]}", "value": round(len(ips)/1000000, 2)})  
    output_json_file = "data/jsons/topCountry.json"
    with open(output_json_file, 'w', encoding='utf-8') as f:
        json.dump(top_cc_result, f, ensure_ascii=False, indent=2)

    # Output top 10 ASN information
    print("Total ASes:", len(asn_dict))
    top_as_result = {"data": [], "unit": "M"}
    top10_asn = sorted(asn_dict.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for asn, ips in top10_asn:
        top_as_result["data"].append({"name": f"AS{asn}-{ASname_dict[asn]}", "value": round(len(ips)/1000000, 2)})
    output_json_file = "data/jsons/topAS.json"
    with open(output_json_file, 'w', encoding='utf-8') as f:
        json.dump(top_as_result, f, ensure_ascii=False, indent=2)

    # Output all CC information
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    all_cc_result = {"title": f"IPv6 Assets by Country Scanned on {date_string} (K)", "data": []}
    for cc, ips in cc_dict.items(): 
        try:
            all_cc_result["data"].append({"name": f"{cc}-{countries_dict[cc]}", "value": round(len(ips)/1000, 2)})
        except KeyError:
            pass    
    output_json_file = "data/jsons/countryAsset.json"
    with open(output_json_file, 'w', encoding='utf-8') as f:
        json.dump(all_cc_result, f, ensure_ascii=False, indent=2)

def reply_type_analysis(filename):
    # 初始化计数器
    count1 = 0
    count3 = 0
    count129 = 0
    countR = 0
    
    lines = open(filename).readlines()
    for line in lines:
        # 分割每行数据
        probe = line.strip().split(',', 1)[1]    
        if probe == "1":
            count1 += 1
        elif probe == "3":
            count3 += 1
        elif probe == "129":
            count129 += 1
        elif probe == "r3" or probe == "r1":
            countR += 1
        
    type_dict = {
        "title": "No. of Each IPv6 Asset Types (M)",
        "data": [
            { "label": "Periphery", "value": round(count1/1000000, 2) },
            { "label": "Middlebox", "value": round(count3/1000000, 2) },
            { "label": "End-host", "value": round(count129/1000000, 2) },
            { "label": "Router", "value": round(countR/1000000, 2) }
        ]
    }
    output_json_file = "data/jsons/assetType.json"
    with open(output_json_file, 'w', encoding='utf-8') as f:
        json.dump(type_dict, f, ensure_ascii=False, indent=2)

def monthly_scan_result(num, filename = "data/jsons/monthlyScan.json"):
    with open(filename, 'r') as file:
        monthly_count = json.load(file)

    now = datetime.now()
    current_month = now.strftime("%m")
    monthly_count["data"].append({"label": f"{current_month}", "value": num})

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(monthly_count, f, ensure_ascii=False, indent=2)
        
def download_table(Hhitlist, num, filename = "data/jsons/scanInfo.json"):
    zip_path = Hhitlist + ".zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(Hhitlist, arcname=Hhitlist)
    
    with open(filename, 'r') as file:
        json_data = json.load(file)
    
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d")

    file_size_bytes = os.path.getsize(zip_path)
    file_size_gb = round(file_size_bytes / (1024 ** 3), 2)
    
    keyword_index = zip_path.find("Hhitlist")
    Hfilename = zip_path[keyword_index:]
    new_data = {
        "scandate": date_string,
        "number": f"{num}M",
        "size": f"{file_size_gb}GB",
        "download": f"http://175.6.54.250/{Hfilename}"
    }

    json_data.append(new_data)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

def copy_and_replace_files(src_folder, dest_folder):
    # 遍历源文件夹中的所有文件
    for filename in os.listdir(src_folder):
        src_file_path = os.path.join(src_folder, filename)
        dest_file_path = os.path.join(dest_folder, filename)
        
        # 检查是否是文件（忽略文件夹）
        if os.path.isfile(src_file_path):
            # 复制文件到目标文件夹，存在同名文件则替换
            shutil.copy2(src_file_path, dest_file_path)
            print(f"Copied and replaced: {src_file_path} to {dest_file_path}")

def move_zip_file(src_folder, dest_folder):
    # 遍历源文件夹中的所有文件
    for filename in os.listdir(src_folder):
        if filename.endswith('.zip'):
            src_file_path = os.path.join(src_folder, filename)
            dest_file_path = os.path.join(dest_folder, filename)
            
            # 移动文件到目标文件夹，存在同名文件则替换
            shutil.move(src_file_path, dest_file_path)
            print(f"Moved: {src_file_path} to {dest_file_path}")


if __name__ == "__main__":
    download() # download Gasser et al.'s hitlist and alias prefixes

    directory = 'data/'
    Ghitlist = directory + get_latest_file_with_date('Ghitlist', directory)
    GaliasPrefix = directory + get_latest_file_with_date('GaliasPrefix', directory)

    APM(Ghitlist, GaliasPrefix)

    get_Hhitlist_low(GaliasPrefix) # extensive collection of seed addresses

    Gseeds = directory + get_latest_file_with_date('Gseeds', directory)
    Hhitlist_low = directory + get_latest_file_with_date('Hhitlist-low', directory)
    file_list = organize_seeds(Gseeds, Hhitlist_low)
    for f in file_list:
        TGA(f, GaliasPrefix)
    
    for f in get_files_with_tga_prefix(directory):
        f = directory + f
        loop_remove_alias(f, GaliasPrefix)

    Hseeds = directory + get_latest_file_with_date('Hseeds', directory)
    yarrp_trace(Hseeds)

    merge_results()
    Hhitlist = directory + get_latest_file_with_date('Hhitlist', directory)
    total = rm_invalid_IP(Hhitlist)
    distribution_analysis(Hhitlist)
    reply_type_analysis(Hhitlist)
    monthly_scan_result(total)
    download_table(Hhitlist, total)

    src_folder = 'data/jsons'  
    dest_folder = '/dabing/vue-ipv6/src/data'  
    copy_and_replace_files(src_folder, dest_folder)
    src_folder = 'data'
    dest_folder = '/dabing/vue-ipv6/public'
    move_zip_file(src_folder, dest_folder)

    HaliasPrefix = directory + get_latest_file_with_date('HaliasPrefix', directory)
    alias_unfile(HaliasPrefix)
