import os
import subprocess

import datetime
import shutil
import time

import logging
logger = logging.getLogger('Benchmarks')

import util.config as config

def submit(directory, folder, index):

    sub_folder = os.path.join(directory, folder)
    for dirname, dirnames, filenames in os.walk(sub_folder):
        current = os.getcwd()
        os.chdir(dirname)
        for filename in filenames:
            if filename.find("script_") == 0:
                logger.info(filename)
                cmd = "sbatch " + filename
                if index % config.submit_jobs == 0:
                    logger.info("waiting 10 seconds...")
                    time.sleep(10)
                try:
                    out = subprocess.check_output([cmd] , shell=True)
                except:
                    logger.error("Cannot submit job "+ cmd)
                #os.system(cmd)
                index+=1
        os.chdir(current)
    return index



def execute(directory, args):

    # Create directory structure
    logger.info(directory)

    index = 1
    if not args.allrack and not args.allswitch and not args.bandwidth and not args.nodes and not args.allpair:

       index = submit(directory,"nodes", index)
       index = submit(directory,"bandwidth", index)
       index = submit(directory,"alltoall_rack", index)
       index = submit(directory,"alltoall_switch", index)
       index = submit(directory,"alltoall_pair", index)

    else:

        if args.allrack==True:
            index = submit(directory,"alltoall_rack", index)
        if args.allswitch==True:
            index = submit(directory,"alltoall_switch", index)
        if args.allpair==True:
            index = submit(directory,"alltoall_pair", index)
        if args.bandwidth==True:
            index = submit(directory,"bandwidth", index)
        if args.nodes==True:
           index = submit(directory,"nodes", index)

    logger.info(str(index-1)+" jobs")
