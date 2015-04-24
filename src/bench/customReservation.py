#######################################################################
##
## Author : Aaron Holt
## Date   : 2-27-2015
## 
## customReservation should allow the user to specify a reservation to
## run in instead of using the next PM reservation.
##
########################################################################

import os
import subprocess
import datetime
import shutil
import textwrap
import re

from hostlist import expand_hostlist
from bench.util.xml2obj import xml2obj

import logging
logger = logging.getLogger(__name__)

##TODO: change the reservation to be a user defined reservation


def reservations():

    reserved_nodes = []
    # scontrol is a slurm command
	# https://computing.llnl.gov/linux/slurm/scontrol.html
	# show <Entity ID>
	# the tag 'res' creates a reservation without specifying a name
	# Reservation=<name>
    p1 = subprocess.Popen(['scontrol','-o', 'show','res'], stdout=subprocess.PIPE)
    # out - contains reservation names and nodes from 'res'
    out, err = p1.communicate()

    reservation_names = re.findall(r'ReservationName=([A-Za-z0-9.\-\_]+)', out)
    reservation_nodes = re.findall(r'Nodes=([,\-A-Za-z0-9\[\]]+)', out)

    for res, nodes in zip(reservation_names, reservation_nodes):
        #print res, expand_hostlist(nodes)
        if (res.endswith('PM-janus') or
           res.endswith('PM-gpu') or
           res.endswith('PM-himem') or
           res.endswith('PM-serial')):
           pass
        else:
        #    print res, expand_hostlist(nodes)
           reserved_nodes.extend(expand_hostlist(nodes))
           logger.info(res.ljust(20)+str(len(expand_hostlist(nodes))).rjust(5))

    logger.info("Total reserved ".ljust(20)+str(len(reserved_nodes)).rjust(5))

    return list(set(reserved_nodes))


def execute(directory,  list, exclude, reservation):

    logger.info(directory)

    logger.info('createing node list')
    free_nodes = free_SLURM_nodes("node[01-17][01-80]")
    reserved_nodes = reservations()

    diff_set = set(free_nodes).difference(set(reserved_nodes))
    node_list = []
    for node in diff_set:
        node_list.append(node)

    logger.info("Available nodes".ljust(20)+str(len(node_list)).rjust(5))

    #Write list to file
    try:
        f = open(os.path.join(directory,'node_list'), 'w')
        for item in node_list:
          f.write("%s\n" % item)
        f.close()
    except:
        logger.error("create: ".rjust(20)+"could not write node_list to file")
