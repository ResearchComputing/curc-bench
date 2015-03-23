import os
import time

import create as create
import submit as submit

import showq as showq
import process as process
import reserve as reserve

import util.config as config

import logging
logger = logging.getLogger('Benchmarks')

def wait_for_jobs():

    logger.info("Waiting for jobs to start")
    time.sleep(60)

    start = time.time()
    # Are we done?
    done = False
    while not done:
        done = showq.evaluate()
        elapsed = (time.time() - start)
        logger.info("elapsed time: ".rjust(20) +  str(round(elapsed/60)).rjust(4) + " minutes")
        if not done:
            time.sleep(config.showq_time)
        elapsed = (time.time() - start)

        if elapsed > config.max_time:
            done = True

def execute(directory, retest):

    logger.info(directory)
    #Create and submit
    create.execute(directory, retest)
    submit.execute(directory)

    # Wait for the jobs to show up in showq
    wait_for_jobs()

    # Process
    process.execute(directory)

    # Create new reservations
    reserve.execute(directory)
