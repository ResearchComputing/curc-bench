#!/usr/bin/env python

import os
import subprocess
import re

from bench.util.hostlist import expand_hostlist
from bench.util.xml2obj import xml2obj

import logging
logger = logging.getLogger('Benchmarks')


def reservations():

    reserved_nodes = []
    ##pyslurm.reservation.get???
    p1 = subprocess.Popen(['scontrol', '-o', 'show', 'res'], stdout=subprocess.PIPE)
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


def free_SLURM_nodes(nodelist):
    node_list = expand_hostlist(nodelist)
    #print len(node_list)

    p1 = subprocess.Popen(['scontrol', '-o', 'show', 'nodes'], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['grep', 'Reason'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    out, err = p2.communicate()

    not_available_nodes = re.findall(r'NodeName=(node[0-9]+)', out)

    diff_set = set(node_list).difference(set(not_available_nodes))
    logger.info("Free nodes".ljust(20)+str(len(diff_set)).rjust(5))
    return diff_set

def execute(directory):

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
        f = open(os.path.join(directory, 'node_list'), 'w')
        for item in node_list:
            f.write("%s\n" % item)
        f.close()
    except:
        logger.error("create: ".rjust(20)+"could not write node_list to file")
