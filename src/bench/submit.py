import os
import subprocess
import time

import logging
logger = logging.getLogger('Benchmarks')

def submit(directory, folder, index, pause):

    sub_folder = os.path.join(directory, folder)
    for dirname, dirnames, filenames in os.walk(sub_folder):
        current = os.getcwd()
        os.chdir(dirname)
        for filename in filenames:
            if filename.find("script_") == 0:
                logger.info(filename)
                cmd = "sbatch " + filename
                #No waiting between job submissions
                if pause == None:
                    try:
                        out = subprocess.check_output([cmd], shell=True)
                    except:
                        logger.error("Cannot submit job "+ cmd)
                    index += 1
                #Wait 10 seconds every pause jobs
                else:
                    if index % pause == 0:
                        logger.info("waiting 10 seconds...")
                        time.sleep(10)
                    try:
                        out = subprocess.check_output([cmd], shell=True)
                    except:
                        logger.error("Cannot submit job "+ cmd)
                    index += 1
        os.chdir(current)
    return index



def execute(directory, allrack=None, allswitch=None, bandwidth=None, nodes=None, allpair=None, pause=None):

    # Create directory structure
    logger.info(directory)

    index = 1
    if not (allrack or allswitch or bandwidth or nodes or allpair):

        index = submit(directory, "nodes", index, pause)
        index = submit(directory, "bandwidth", index, pause)
        index = submit(directory, "alltoall_rack", index, pause)
        index = submit(directory, "alltoall_switch", index, pause)
        index = submit(directory, "alltoall_pair", index, pause)

    else:

        if allrack == True:
            index = submit(directory, "alltoall_rack", index, pause)
        if allswitch == True:
            index = submit(directory, "alltoall_switch", index, pause)
        if allpair == True:
            index = submit(directory, "alltoall_pair", index, pause)
        if bandwidth == True:
            index = submit(directory, "bandwidth", index, pause)
        if nodes == True:
            index = submit(directory, "nodes", index, pause)

    logger.info(str(index-1)+" jobs")
