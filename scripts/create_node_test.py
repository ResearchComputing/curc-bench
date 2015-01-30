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
       
        

current_path = os.getcwd()
source_path = sys.path[0]

if len(sys.argv) == 1:
    node_list = "node[01-17][01-80]"
    r = listPBSnodes(node_list)

if len(sys.argv) == 2:
    if os.path.exists(sys.argv[1]):
        r = read_nodes_from_file(sys.argv[1])
    else:
        node_list = sys.argv[1]
        r = freePBSnodes(node_list)
        
for node in r:
    print str(node)
    
    # create the pbs command
    #filename = os.path.join(current_path,"script_" + node)
    #template_pbs = os.path.join(source_path,"template_single_node.pbs")
    #cmd = "cat " + template_pbs + " | sed s/\<NODE_NAME\>/" + node + "/ > " + filename 
    #os.system(cmd)
