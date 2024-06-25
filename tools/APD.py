# coding=utf-8
import random
from multiping import multi_ping
from datetime import datetime
import math
import sys

try:
    import SubnetTree
except Exception as e:
    print(e, file=sys.stderr)
    print("use `pip3 install pysubnettree` to install the required module", file=sys.stderr)
    sys.exit(1)

def bu0(dizhi):
    dizhi1 = dizhi.split(':')
    for i in range(0, len(dizhi1)):
        # 小段地址补0 如 :AB: 补成:00AB:
        if ((len(dizhi1[i]) < 4) and (len(dizhi1[i]) > 0)):
            temp = dizhi1[i]
            # 需补0数
            que0 = 4 - len(dizhi1[i])
            temp2 = "".join('0' for i in range(0, que0))
            dizhi1[i] = temp2 + temp

    # 补 ::中的0, count为补完:中0后长度
    count = 0
    for i in range(0, len(dizhi1)):
        count = count + len(dizhi1[i])
    count = 32 - count
    aa = []
    aa = ''.join('0' for i in range(0, count))
    for i in range(1, len(dizhi1) - 1):
        if len(dizhi1[i]) == 0:
            dizhi1[i] = aa
    for i in range(len(dizhi1)):
        bb = ''.join(sttt for sttt in dizhi1)
    return bb


def legal(dizhi):
    dizhi1 = dizhi.split('::')
    label = 1

    # 使用::不能大于2次
    if len(dizhi1) >= 3:
        label = 0
    else:
        # 字符范围应为 0~9 A~F
        for i, char in enumerate(dizhi):
            if char not in ':0123456789abcdef':
                label = 0
    # :不能出现在末位 同时允许::在最后
    # :不能出现在首位 同时允许::在最前
    if (dizhi[len(dizhi) - 1] == ':') and (dizhi[len(dizhi) - 2] != ':'):
        label = 0
    if (dizhi[0] == ':') and (dizhi[1] != ':'):
        label = 0

    # 不能出现 :::
    temp3 = dizhi.split(":::")
    if len(temp3) > 1:
        label = 0

    # 每小节位数应不大于4
    dizhi2 = dizhi.split(':')
    for i in range(0, len(dizhi2)):
        if len(dizhi2[i]) >= 5:
            label = 0

    if label == 0:
        print("error IP:", dizhi)
    return label

def iptrans(line):
    line = line.strip()
    if legal(line):
        out = bu0(line)
        return out
    else:
        return ''

def iplisttrans(ipl):
    addrs = []
    for line in ipl:
        line = line.strip()
        if legal(line):
            out = bu0(line)
            addrs.append(out)
    return addrs

def retrans(lines):
    colons=[]
    for line in lines:
        lout=list(line)
        for i in range(4,35,5):
            lout.insert(i,":")
        lout="".join(lout)
        colons.append(lout)
    return colons

def num_to_string(num):
    numbers = {
        0 : "0",
        1 : "1",
        2 : "2",
        3 : "3",
        4 : "4",
        5 : "5",
        6 : "6",
        7 : "7",
        8 : "8",
        9 : "9",
        10 : "a",
        11 : "b",
        12 : "c",
        13 : "d",
        14 : "e",
        15 : "f"
    }
    return numbers.get(num, None)

def genaddr(lenth):
    rangenum=(16**lenth)-1
    ranip=random.randint(0, rangenum)
    hexip=hex(ranip)
    if hexip[-1]=='L':
        hexip=hexip[:-1]
    c=hexip[2:].zfill(lenth)
    return c

def APD(filename): # Discover missed alias-prefix from results
    lines = open(filename).readlines()

    responder_list = list()
    for line in lines:
        if line[0] != '#':
            if line.find(',') != -1:
                split_strings = line.split(',')
                responder = split_strings[0].strip()
                responder_list.append(iptrans(responder))
            else:
                responder = line.strip()
                responder_list.append(iptrans(responder))
    
    prefixes = list()
    ips=list()
    for lent in range(8, 26): # Traverse prefixes from 32 to 112
        total = 0
        prefix_dict = dict()
        for line in responder_list:
            if line[:lent] not in prefix_dict.keys():
                prefix_dict[line[:lent]] = 0
            prefix_dict[line[:lent]] += 1
        total = sum(list(prefix_dict.values()))
        prefix_tuple=zip(prefix_dict.values(),prefix_dict.keys())
        prefix_list=list(sorted(prefix_tuple, reverse=True))
        prefixes.append(prefix_list[0][1])
        print(prefix_list[0][1], prefix_list[0][0], round(prefix_list[0][0]*100/total, 2), '%')
        if round(prefix_list[0][0]*100/total, 2) < 0.1:
            break
        if len(prefix_list) >= 2:
            prefixes.append(prefix_list[1][1])
            print(prefix_list[1][1], prefix_list[1][0], round(prefix_list[1][0]*100/total, 2), '%')
        if len(prefix_list) >= 3:
            prefixes.append(prefix_list[2][1])
            print(prefix_list[2][1], prefix_list[2][0], round(prefix_list[2][0]*100/total, 2), '%')
    print("begin pinging the prefixes:")
    print(prefixes)

    for prefix in prefixes:
        ips16=[]
        for bit in range(0,16):
            pre = prefix + num_to_string(bit)
            addr = genaddr(32-len(pre))
            ip = pre + addr
            ips16.append(ip)
        ips.append(ips16)

    prefixlist=[]
    for ips16 in ips:
        responses, no_responses = multi_ping(retrans(ips16), timeout=1, retry=2)
        if len(responses) > 2: #16
            print('# IPs:', len(ips16), '# responses:', len(responses))
            res=[]
            for addr, rtt in responses.items():
                # print "%s responded in %f seconds" % (addr, rtt)
                res.append(addr)
            nor = iplisttrans(res)
            for lent in range(25,7,-1):
                prefix_set = set([line[:lent] for line in nor])
                if len(prefix_set)==1:
                    print("alias prefix:", prefix_set)
                    prefixlist.extend(list(prefix_set))
                    break

    alias = []
    for line in prefixlist:
        prefixlen = len(line)*4
        line = line + '0' * (32 - len(line))
        lout=list(line)
        for i in range(4,35,5):
            lout.insert(i,":")
        lout="".join(lout)
        ln = "/" + str(prefixlen)
        lout = lout + ln
        # print(f'alias prefix: {lout}')
        alias.append(lout)
    if len(alias):
        # 获取当前日期和时间
        now = datetime.now()
        # 格式化日期为字符串，例如 "2023-05-21"
        date_string = now.strftime("%Y-%m-%d")
        afilename = f"data/HaliasPrefix_{date_string}"
        with open(afilename, "a") as file:
            file.writelines(line + "\n" for line in alias)
        return 1
    return 0

def alias_unfile(filename):
    lines = open(filename).readlines()
    alias = list()
    prefix_dict = dict()    
    for lent in range(7, 31):
        prefix_dict[lent] = set()    
        
    for line in lines:
        if line[0]!='#':
            index = line.find('/')
            prefix_len = int(line[index+1:-1])//4
            if prefix_len > 30:
                print('Error:', line)
                continue
            prefix = iptrans(line[:index])[:prefix_len]
            prefix_dict[prefix_len].add(prefix)

    prefix2remove = list()
    for lent1 in range(30, 7, -1):
        for prefix2detect in prefix_dict[lent1]:
            for lent2 in range(7, lent1):
                for prefix_father in prefix_dict[lent2]:
                    if prefix2detect.find(prefix_father) == 0:
                        prefix2remove.append(prefix2detect)
                        # print("Remove prefix:", prefix2detect, "as contains its parent prefix of:", prefix_father)
    for prefix_redundancy in set(prefix2remove):
        prefix_dict[len(prefix_redundancy)].remove(prefix_redundancy)
    
    prefix_sum = 0   
    for k, v in prefix_dict.items():
        for line in v:
            x=int(math.ceil(float(len(line))/4-1))
            y=len(line)%4
            li=list(line)
            for i in range(4, x*5, 5):
                li.insert(i, ":")
            li = "".join(li)
            add_zero = 4 - len(li[(li.rfind(':')+1):])
            if len(line) <= 28:
                ln = '0'*add_zero + "::/" + str(len(line)*4)
            else:
                ln = '0'*(32-len(line))+'/'+str(len(line)*4)
            li = li + ln
            alias.append(li)
        prefix_sum += len(v)
    print("Reduce", len(lines), "prefixes to", prefix_sum)   
    with open(filename, "w") as file:
            file.writelines(line + "\n" for line in alias)

# def re_APD(filename):
#     alias_list = open(filename).readlines()
#     arrange_prefix = list()
#     for prefix in alias_list:
#         temp = prefix
#         prefix = prefix[:prefix.index('/')].replace(':','') 
#         remainder = len(prefix)%4
#         if remainder:
#             str1 = list()
#             index = temp.find('::/')
#             for i in range(4-remainder):
#                 str1.append('0')
#                 add_zero = ''.join(str1)
#             temp = temp[:index] + add_zero + temp[index:]
#         arrange_prefix.append(temp)

#     final_arrange_prefix = arrange_prefix
#     res_dict = dict()
#     for prefix in arrange_prefix:
#         temp = prefix
#         prefix_len = math.ceil(int(prefix[prefix.index('/')+1 : -1])/4)
#         prefix = prefix[:prefix.index('/')].replace(':','')    
#         if (len(prefix) > prefix_len):
#             prefix = prefix[:prefix_len]
#         ips16=[]
#         for bit in range(0,16):
#             pre = prefix + num_to_string(bit)
#             addr = genaddr(32-len(pre))
#             ip = pre + addr
#             ips16.append(ip)

#         responses, no_responses = multi_ping(retrans(ips16), timeout=1, retry=2)
#         print(temp[:-1], 'has', len(responses), 'responses')

#         if len(responses) not in res_dict.keys():
#             res_dict[len(responses)] = 0
#         res_dict[len(responses)] += 1

#         if len(responses) == 0: # Remove prefixes that can never be alias prefixes
#             final_arrange_prefix.remove(temp)

#     res_dict = sorted(res_dict.items(), key=lambda x:x[0], reverse=True)
#     res_dict = dict([res_dict[i] for i in range(len(res_dict))])
#     for k, v in res_dict.items():
#         print('responses:', k, 'ratio:', round(v*100.0/len(arrange_prefix), 2), '%')

#     f = open(filename,"w")
#     f.writelines(final_arrange_prefix)
#     f.close() 

def read_aliased(tree, fh):
    return fill_tree(tree, fh, ",1")

def fill_tree(tree, fh, suffix):
    for line in fh:
        line = line.strip()
        try:
            tree[line] = line + suffix
        except ValueError as e:
            print("skipped line '" + line + "'", file=sys.stderr)
    return tree

def APM(IPf, af): # alias prefixes match

    # Store alias prefixes in a single subnet tree
    tree = SubnetTree.SubnetTree()

    # Read alias prefixes
    aflines = open(af).readlines()    
    tree = read_aliased(tree, aflines)

    # Read IP address file, match each address to longest prefix
    IPflines = open(IPf).readlines() 
    print("total IP addresses:", len(IPflines))
    nonalias = []

    for line in IPflines:
        templine = line.strip()
        if ',' in templine:
            templine = line.split(',', 1)[0]
        try:
            tree[templine]
        except KeyError:
            nonalias.append(line)

    nonalias = list(set(nonalias))
    print("non-alias IP addresses:", len(nonalias))

    newf = IPf
    if 'Ghitlist' in IPf:
        newf = IPf.replace("Ghitlist", "Gseeds")
    if "TGA" in IPf and "TGA-APD" not in IPf:
        newf = IPf.replace("TGA", "TGA-APD")

    with open(newf, 'w') as file:
        file.writelines(nonalias)

    return newf