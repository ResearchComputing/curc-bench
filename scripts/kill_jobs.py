#!/curc/admin/benchmarks/bin/python
import os

cmd = "qstat | grep molu | cut -f1 -d. > tmp_jobs"
cmd = "showq | grep molu | cut -f1 -d. > tmp_jobs"

os.system(cmd)
job_ids = open("tmp_jobs","r")
while job_ids:
    id = job_ids.readline()
    if not id:
        break
    cmd = "canceljob " + id
    os.system(cmd)

job_ids.close()
