import os
import subprocess
import time

import logging
logger = logging.getLogger('Benchmarks')

def submit(directory, folder, index, pause, reservation, qos, account):

    sub_folder = os.path.join(directory, folder)
    for dirname, dirnames, filenames in os.walk(sub_folder):
        current = os.getcwd()
        os.chdir(dirname)
        for filename in filenames:
            if filename.find("script_") == 0:
                logger.info(filename)
                cmd = "sbatch"
                #User specified reservation, qos, account?
                if reservation != None:
                    cmd = cmd + " + --reservation=" + reservation
                if qos != None:
                    cmd = cmd + " + --qos=" + qos
                if account != None:
                    cmd + " + --account=" + account
                cmd = cmd + " " + filename
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


def execute(directory, pause=None, reservation=None, qos=None, account=None,
            allrack=None, allswitch=None, bandwidth=None, nodes=None, allpair=None):
            
    # Create directory structure
    logger.info(directory)

    index = 1
    if not (allrack or allswitch or bandwidth or nodes or allpair):

        index = submit(directory, "nodes", index, pause, reservation, qos, account)
        index = submit(directory, "bandwidth", index, pause, reservation, qos, account)
        index = submit(directory, "alltoall_rack", index, pause, reservation, qos, account)
        index = submit(directory, "alltoall_switch", index, pause, reservation, qos, account)
        index = submit(directory, "alltoall_pair", index, pause, reservation, qos, account)

    else:

        if allrack == True:
            index = submit(directory, "alltoall_rack", index, pause, reservation, qos, account)
        if allswitch == True:
            index = submit(directory, "alltoall_switch", index, pause, reservation, qos, account)
        if allpair == True:
            index = submit(directory, "alltoall_pair", index, pause, reservation, qos, account)
        if bandwidth == True:
            index = submit(directory, "bandwidth", index, pause, reservation, qos, account)
        if nodes == True:
            index = submit(directory, "nodes", index, pause, reservation, qos, account)

    logger.info(str(index-1)+" jobs")
