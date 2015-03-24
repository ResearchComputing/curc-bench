import os
import time
import subprocess

def execute(directory):

    filename = os.path.join(directory,'bench.log')
    out = subprocess.check_output(["cat %s" % filename] , shell=True)
    print out
