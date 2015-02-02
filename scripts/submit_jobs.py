#!/curc/admin/benchmarks/bin/python
import os

for dirname, dirnames, filenames in os.walk('.'):
    for filename in filenames:
        if filename.find("script_") == 0:
            print filename
            cmd = "qsub " + filename
            os.system(cmd)
