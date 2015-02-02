#!/curc/admin/benchmarks/bin/python
import os

os.system("pdsh -w node[01-17][01-80] 'killall -u molu8455'")
