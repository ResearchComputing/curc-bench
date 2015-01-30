#!/curc/admin/benchmarks/bin/python
import os, sys

filename = sys.argv[1]

cmd = "export NODE_LIST="
job_ids = open(filename,"r")
while job_ids:
    id = job_ids.readline()
    if not id:
        break
    tmp = id.split()
    if len(tmp):
         cmd = cmd + str(tmp[0]) + ","
job_ids.close()   

# create ENV variable
print cmd[:-1]
print "mrsvctl -c -h $NODE_LIST -n 'benchmark-node' -a USER==molu8455"



