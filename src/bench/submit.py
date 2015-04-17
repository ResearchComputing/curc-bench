import logging
import os
import subprocess
import time


if not hasattr(subprocess, 'check_output'):
    import bench.util
    bench.util.patch_subprocess_check_output()


logger = logging.getLogger('Benchmarks')


def submit(directory, folder, index, pause, reservation, qos, account):
    sub_folder = os.path.join(directory, folder)
    for dirname, dirnames, filenames in os.walk(sub_folder):
        current = os.getcwd()
        os.chdir(dirname)
        for filename in filenames:
            if filename.find("node") == 0:
                logger.info(filename)
                cmd = "sbatch"
                #User specified reservation, qos, account?
                if reservation != False and reservation != None:
                    cmd = cmd + " --reservation=" + reservation
                if qos != False and qos != None:
                    cmd = cmd + " --qos=" + qos
                if account != False and qos != None:
                    cmd = cmd + " --account=" + account
                cmd = cmd + " " + filename
                #User specified to wait between 'pause' job submissions?
                if pause != None and pause != 0:
                    if index % pause == 0:
                        logger.info("waiting 10 seconds...")
                        time.sleep(10)
                try:
                    out = bench.util.subprocess.check_output([cmd], shell=True)
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

        index = submit(directory, "node", index, pause, reservation, qos, account)
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
            index = submit(directory, "node", index, pause, reservation, qos, account)

    logger.info(str(index-1)+" jobs")
