#!/curc/admin/benchmarks/bin/python
import os, sys
from pandas import *

def build_results_file():
    out_file = open("results","w")
    data_line = ""
    data_line += "s1,s2,s3,s4,"
    data_line += "t1,l1,t2,l2,t3,l3,t4,l4,t5,l5,t6,l6"
    out_file.write(data_line)
    out_file.write("\n")
    
    for dirname, dirnames, filenames in os.walk('.'):
        for subdirname in dirnames:
            if subdirname.find("node") == 0:
                data_line = subdirname + ", "
                in_file = open(os.path.join(subdirname,"data"),"r")
                if not in_file:
                    break
                '''    
                # IOR data
                test = in_file.readline().split()[0]
                data = in_file.readline().split()
                if not data:
                    print data_line
                    continue
                data_line += data[1] + " " 
                data_line += data[2] + " "    
                data_line += data[3] + " " 
                '''
            
                # Stream data
                test = in_file.readline().split()[0]
                data = in_file.readline().split()
                if not data:
                    print data_line
                    continue
                data_line += data[0] + ","
                data_line += data[1] + ","   
                data_line += data[2] + ","    
                data_line += data[3] 
            
                # Linpack data
                data = in_file.readline()
                data = in_file.readline()
                data = in_file.readline()
                data = in_file.readline()
            
                data = in_file.readline().split()
                if not data:
                    print data_line
                    continue
            
                while data:
                    data_line += "," + data[0] + "," + data[3] 
                    data = in_file.readline().split()
          
                in_file.close()
                out_file.write(data_line)
                out_file.write("\n")            
    out_file.close()

def find_percent(pvalue):
    print "finding " + str(pvalue) + " pecent"
    df = read_csv("results", index_col=0, header=0)
    
    # write the mean to a file
    df = df[['s1','s2','s3','s4','l3','l4','l5','l6']]
    pdiff = ((df - df.mean(0)) / df.mean(0))*100
   
    threshold = -1.0*pvalue
    pdiff_concern = pdiff.applymap(lambda x: x if x < threshold else 0)
    pdiff_check = pdiff_concern[pdiff_concern.sum(1) < 0]
    
    bad_nodes = []
    for i, row in enumerate(pdiff_check.values):
        bad_nodes.append(pdiff_check.index[i])
    
    print "---------------------------------------"
    print "bad nodes"
    print "---------------------------------------"
    for i in set(bad_nodes):
        print i
    print "---------------------------------------"
    
    
    if pdiff_check:
        print pdiff_check
    else:
        print "No errors found"

def find_mean_percent(filename, pvalue):
    print "comparing with mean from file = " + filename
    print "finding " + str(pvalue) + " pecent"
    dfc = read_csv(filename, index_col=0, header=0)
    dfc = dfc[['s1','s2','s3','s4','l3','l4','l5','l6']]
    
    df = read_csv("results", index_col=0, header=0)
    df = df[['s1','s2','s3','s4','l3','l4','l5','l6']]
    
    pdiff = ((df - dfc.mean(0)) / dfc.mean(0))*100
    threshold = -1.0*pvalue
    pdiff_concern = pdiff.applymap(lambda x: x if x < threshold else 0)
    pdiff_check = pdiff_concern[pdiff_concern.sum(1) < 0]
    
    bad_nodes = []
    for i, row in enumerate(pdiff_check.values):
        bad_nodes.append(pdiff_check.index[i])
    
    print "---------------------------------------"
    print "bad nodes"
    print "---------------------------------------"
    for i in set(bad_nodes):
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



