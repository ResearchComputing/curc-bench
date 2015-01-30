#!/curc/admin/benchmarks/bin/python
import os
from pandas import *

def build_results_file():
    out_file = open("bandwidth_results","w")
    out_file.write("nodes node1 node2 1 2 4 8 16 32 64 128 256 512 1024 2048 4096 8192 16384 32768 65536 131072 262144 524288 1048576 2097152 4194304 ")
    out_file.write("\n")

    for dirname, dirnames, filenames in os.walk('.'):
        for subdirname in dirnames:
            if subdirname.find("job_node") == 0:
            
                # Did the run finish?
                if os.path.exists(os.path.join(subdirname,"data_done")) :
                
                    #bw data
                    in_file = open(os.path.join(subdirname,"data_bw"),"r")
                    node_name = subdirname[4:]
                    node_one = node_name[:8]
                    node_two = node_name[9:]
                
                    out_file.write(node_name + " " + node_one + " " + node_two + " ")
                    print node_name
                    while in_file:
                        line = in_file.readline()
                        split = line.split()
                        if not split:
                            break
                        if split[0] == '#':
                            continue
                        out_file.write(split[1] + " ")
                                        
                    in_file.close()
                    out_file.write("\n")    
    out_file.close()

def find_percent(pvalue):
    print "finding " + str(pvalue) + " pecent"
    df = read_csv("bandwidth_results", index_col=0, header=0)
    print df
    # write the mean to a file
    df = df[['s1','s2','s3','s4','l3','l4','l5','l6']]
    pdiff = ((df - df.mean(0)) / df.mean(0))*100
   
    threshold = -1.0*pvalue
    pdiff_concern = pdiff.applymap(lambda x: x if x < threshold else 0)
    pdiff_check = pdiff_concern[pdiff_concern.sum(1) < 0]
    
    
    if pdiff_check:
        print pdiff_check
    else:
        print "No errors found"

build_results_file()
find_percent(10)




