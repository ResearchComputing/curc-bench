import os
import subprocess
import time

import logging
logger = logging.getLogger('Benchmarks')

def submit(directory, folder, index, pause, reservation):

    sub_folder = os.path.join(directory, folder)
    for dirname, dirnames, filenames in os.walk(sub_folder):
        current = os.getcwd()
        os.chdir(dirname)
        for filename in filenames:
            if filename.find("script_") == 0:
                logger.info(filename)
                #User specified reservation?
                if reservation == None:
                    cmd = "sbatch " + filename
                else:
                    cmd = "sbatch + --reservation=" + reservation + " " + filename
                #User specified to wait between 'pause' job submissions?
                if pause != None:
                    if index % pause == 0:
                        logger.info("waiting 10 seconds...")
                        time.sleep(10)
                try:
                    out = subprocess.check_output([cmd], shell=True)
                except:
                    logger.error("Cannot submit job " + cmd)
                index += 1

        os.chdir(current)
    return index



def execute(directory, allrack=None, allswitch=None, bandwidth=None, 
            nodes=None, allpair=None, pause=None, reservation=None):

    # Create directory structure
    logger.info(directory)

    index = 1
    if not (allrack or allswitch or bandwidth or nodes or allpair):

        index = submit(directory, "nodes", index, pause, reservation)
        index = submit(directory, "bandwidth", index, pause, reservation)
        index = submit(directory, "alltoall_rack", index, pause, reservation)
        index = submit(directory, "alltoall_switch", index, pause, reservation)
        index = submit(directory, "alltoall_pair", index, pause, reservation)

    else:

        if allrack == True:
            index = submit(directory, "alltoall_rack", index, pause, reservation)
        if allswitch == True:
            index = submit(directory, "alltoall_switch", index, pause, reservation)
        if allpair == True:
            index = submit(directory, "alltoall_pair", index, pause, reservation)
        if bandwidth == True:
            index = submit(directory, "bandwidth", index, pause, reservation)
        if nodes == True:
            index = submit(directory, "nodes", index, pause, reservation)

    logger.info(str(index-1)+" jobs")
