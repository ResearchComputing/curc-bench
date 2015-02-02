#!/curc/admin/benchmarks/bin/python

import os
import sys
import shutil
from pbs import freePBSnodes, listPBSnodes

def read_nodes_from_file(filename):
    node_list = []
    in_file = open(filename,"r")
    while in_file:
        node = in_file.readline()
        if not node:
            break
        line = node.split()
        if not line:
            break
        node_list.append(line[0])

    return node_list

def create_node_pairs(node_list):
    pair_list = []

    odd_list = node_list[::2]
    even_list = node_list[1::2]

    tmp1 = odd_list[0]
    if len(odd_list) > len(even_list):
        tmp1 = odd_list.pop(len(odd_list)-1)

    # create list
    for i in range(len(odd_list)):
        node_pair = odd_list[i], even_list[i]
        node_pair = sorted(node_pair)
        if node_pair not in pair_list:
            pair_list.append(node_pair)

    # create second list
    odd_list.append(tmp1)
    tmp2 = odd_list.pop(0)

    for i in range(len(odd_list)):
        node_pair = odd_list[i], even_list[i]
        node_pair = sorted(node_pair)
        if node_pair not in pair_list:
            pair_list.append(node_pair)

    # add the last pair if odd size list
    if tmp1 != tmp2:
        node_pair = tmp1, tmp2
        node_pair = sorted(node_pair)
        pair_list.append(node_pair)

    return sorted(pair_list)

def create_single_script(node_name, node_list):

    filename = os.path.join(current_path,"script_" + node_name)
    template_pbs = os.path.join(source_path,"template_bandwidth.pbs")
    cmd = "cat " + template_pbs + " | sed s/\<NODE_LIST\>/" + node_list + "/ > " +  filename + ".1"
    os.system(cmd)

    job_name = "job_" + node_name
    cmd = "cat " + filename + ".1 | sed s/\<JOB_NAME\>/" + job_name + "/ > " +  filename
    os.system(cmd)
    os.system("rm -rf *.1")

def create_pbs_scripts(pair_list):
    for pair in pair_list:
        node_list = pair[0] + ":ppn=12+" + pair[1] + ":ppn=12"
        node_name = pair[0] + "-" + pair[1]

        print node_name
        create_single_script(node_name, node_list)

current_path = os.getcwd()
source_path = sys.path[0]

# 0201 - 0280, 301 special
# 01* long
#




if len(sys.argv) == 1:
    # long
    node_list = "node[01][01-80]"
    r = freePBSnodes(node_list)
    pair_list = create_node_pairs(r)
    create_pbs_scripts(pair_list)

    # special
    node_list = "node[02][01-80]"
    r = freePBSnodes(node_list)
    tmp = freePBSnodes("node[03][01]")
    r.append(tmp[0])
    pair_list = create_node_pairs(r)
    create_pbs_scripts(pair_list)

    # janus
    node_list = "node[04-17][01-80]"
    r = freePBSnodes(node_list)
    pair_list = create_node_pairs(r)
    create_pbs_scripts(pair_list)

    node_list = "node[03][02-80]"
    r = freePBSnodes(node_list)
    pair_list = create_node_pairs(r)
    create_pbs_scripts(pair_list)

if len(sys.argv) == 2:
    if os.path.exists(sys.argv[1]):
        r = read_nodes_from_file(sys.argv[1])
        pair_list = create_node_pairs(r)
        create_pbs_scripts(pair_list)

    else:
        node_list = sys.argv[1]
        r = freePBSnodes(node_list)
        pair_list = create_node_pairs(r)
        create_pbs_scripts(pair_list)




#for node in r:
#    print str(node)

    # create the pbs command
    #filename = os.path.join(current_path,"script_" + node)
    #template_pbs = os.path.join(source_path,"template_bandwdith_node.pbs")
    #cmd = "cat " + template_pbs + " | sed s/\<NODE_NAME\>/" + node + "/ > " + filename
    #os.system(cmd)
