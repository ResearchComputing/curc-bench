#!/usr/bin/env python

from bench.util.hostlist import expand_hostlist
import logging
import os
import pyslurm
import re


logger = logging.getLogger('Benchmarks')


PM_RESERVATIONS_P = re.compile(r'^.*PM-(janus|gpu|himem|serial|ipcc)$')


def get_reserved_nodes():

    reserved_nodes = set()

    reservations = pyslurm.reservation()
    for reservation_name, reservation in reservations.get().iteritems():
        if PM_RESERVATIONS_P.match(reservation_name):
            continue
        elif 'node_list' not in reservation:
            continue
        else:
            print reservation_name
            reserved_nodes.update(set(expand_hostlist(reservation['node_list'])))

    logger.info("nodes reserved: {0}".format(len(reserved_nodes)))
    return list(reserved_nodes)


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
    reserved_nodes = get_reserved_nodes()

    diff_set = set(free_nodes).difference(set(reserved_nodes))
    node_list = []
    for node in diff_set:
        node_list.append(node)

    logger.info("Available nodes".ljust(20)+str(len(node_list)).rjust(5))

    try:
        f = open(os.path.join(directory, 'node_list'), 'w')
        for item in node_list:
            f.write("%s\n" % item)
        f.close()
    except:
        logger.error("create: ".rjust(20)+"could not write node_list to file")
