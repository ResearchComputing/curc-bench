#!/usr/bin/env python

import os
# import subprocess
# import re
import pyslurm

from bench.util.hostlist import expand_hostlist

import logging
logger = logging.getLogger('Benchmarks')


def reservations():

    b = pyslurm.reservation()
    reserve_dict = b.get()
    slurm_reserve_nodes = set([])

    for key, value in reserve_dict.iteritems():
        #Don't add following to reserved nodes
        if (key.endswith('PM-janus') or key.endswith('PM-gpu') or
                key.endswith('PM-himem') or key.endswith('PM-serial')):
            #print "Not used = ","%s :" % (key)
            pass
        #Add every other reservation to reserved nodes
        else:
            #print "Used = ","%s :" % (key)
            for part_key in sorted(value.iterkeys()):
                #print "\t%-15s : %s" % (part_key, value[part_key])
                if part_key == 'node_list':
                    #if value[part_key][0:4] == 'node':
                    nodes = expand_hostlist(value[part_key])
                    for node in nodes:
                        slurm_reserve_nodes.add(node)

    logger.info("Total reserved ".ljust(20)+str(len(slurm_reserve_nodes)).rjust(5))
    return list(slurm_reserve_nodes)


def free_SLURM_nodes():

    a = pyslurm.node()
    node_dict = a.get()
    slurm_free_nodes = set([])

    for key, value in node_dict.iteritems():
        #print "%s :" % (key)
        for part_key in sorted(value.iterkeys()):
            #if key == 'node0903' or key == 'node0805':
                #print "\t%-15s : %s" % (part_key, value[part_key])s
            if part_key == 'node_state':
                #print "%s :" % (key), "    node_state = ",value[part_key]
                if (value[part_key] == 'IDLE' or value[part_key] == 'ALLOCATED' or
                      value[part_key] == 'COMPLETING' or value[part_key] == 'RESERVED'):
                    if key[0:4] == 'node':
                        if int(key[4:6]) >= 01 and int(key[4:6]) <= 17:
                            if int(key[6:8]) >= 01 and int(key[6:8]) <= 80:
                                slurm_free_nodes.add(key)

    logger.info("Free nodes".ljust(20)+str(len(slurm_free_nodes)).rjust(5))
    return slurm_free_nodes

def execute(directory):

    logger.info(directory)

    logger.info('createing node list')
    # free_nodes = free_SLURM_nodes("node[01-17][01-80]")
    free_nodes = free_SLURM_nodes()
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
