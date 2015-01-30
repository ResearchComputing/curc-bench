#!/curc/admin/benchmarks/bin/python
import os

time = "72000"
last = 18

for i in range(1,last):
    nodenum = str(i)
    if i < 10:
        nodenum = "0" + str(i)
        
    cmd =  "pdsh  -w  node" + nodenum + "[01-20] '. /curc/tools/utils/dkinit; use TeachingHPC; mpirun -np 12 /curc/admin/benchmarks/software/load/burn " + time + "; echo done' &"
    print cmd
    os.system(cmd)
    cmd =  "pdsh  -w  node" + nodenum + "[21-40] '. /curc/tools/utils/dkinit; use TeachingHPC; mpirun -np 12 /curc/admin/benchmarks/software/load/burn " + time + "; echo done' &"
    print cmd
    os.system(cmd)
    cmd =  "pdsh  -w  node" + nodenum + "[41-60] '. /curc/tools/utils/dkinit; use TeachingHPC; mpirun -np 12 /curc/admin/benchmarks/software/load/burn " + time + "; echo done' &"
    print cmd
    os.system(cmd)
    cmd = "pdsh  -w  node" + nodenum + "[61-80] '. /curc/tools/utils/dkinit; use TeachingHPC; mpirun -np 12 /curc/admin/benchmarks/software/load/burn " + time + "; echo done' &"
    print cmd
    os.system(cmd)
    
print "done"
