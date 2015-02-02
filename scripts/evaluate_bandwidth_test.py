#!/curc/admin/benchmarks/bin/python
import os, sys
from pandas import *

def build_results_file():
    out_file = open("bandwidth_results","w")
    #out_file.write(" node1, node2, x1, x2, x4, x8, x16, x32, x64, x128, x256, x512, x1024, x2048, x4096, x8192, x16384, x32768, x65536, x131072, x262144, x524288, x1048576, x2097152, x4194304")
    out_file.write("node1,node2,x1,x2,x4,x8,x16,x32,x64,x128,x256,x512,x1024,x2048,x4096,x8192,x16384,x32768,x65536,x131072,x262144,x524288,x1048576,x2097152,x4194304")
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

                    out_file.write(node_name + "," + node_one + "," + node_two )
                    #out_file.write(node_name )
                    print node_name
                    while in_file:
                        line = in_file.readline()
                        split = line.split()
                        if not split:
                            break
                        if split[0] == '#':
                            continue
                        out_file.write("," + split[1] )

                    in_file.close()
                    out_file.write("\n")
    out_file.close()

def find_percent(pvalue):
    print "finding " + str(pvalue) + " pecent"
    df = read_csv("bandwidth_results", index_col=0)
    print df
    ndf = df[['x131072','x262144','x524288','x1048576','x2097152','x4194304']]

    pdiff = ((ndf - ndf.mean(0)) / ndf.mean(0))*100
    threshold = -1.0*pvalue
    pdiff_concern = pdiff.applymap(lambda x: x if x < threshold else 0)
    pdiff_check = pdiff_concern[pdiff_concern.sum(1) < 0]
    pdiff_check_names = df[pdiff_concern.sum(1) < 0]
    bad_nodes = []
    for i, row in enumerate(pdiff_check_names.values):
        bad_nodes.append(row[0])
        bad_nodes.append(row[1])

    really_bad_nodes = []
    print bad_nodes
    for i in set(bad_nodes):
        if bad_nodes.count(i) == 2:
            really_bad_nodes.append(i)
    print "---------------------------------------"
    print "bad nodes"
    print "---------------------------------------"
    for i in set(bad_nodes):
        print i
    print "---------------------------------------"
    print "bad nodes really"
    print "---------------------------------------"
    for i in set(really_bad_nodes):
        print i
    print "---------------------------------------"

    if pdiff_check:
        print pdiff_check
    else:
        print "No errors found"




build_results_file()
if len(sys.argv) == 1:
    find_percent(10)

if len(sys.argv) == 2:
    if os.path.exists(sys.argv[1]):
        find_mean_percent(sys.argv[1], 10)
    else:
        pval = float(sys.argv[1])
        find_percent(pval)

if len(sys.argv) == 3:
    if os.path.exists(sys.argv[1]):
        find_mean_percent(sys.argv[1], float(sys.argv[2]))
    else:
        find_mean_percent(sys.argv[2], float(sys.argv[1]))
