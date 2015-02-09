#!/usr/bin/env python

import os
import subprocess
import datetime
import shutil
import textwrap
import re

from util.hostlist import expand_hostlist
from util.xml2obj import xml2obj

import logging
logger = logging.getLogger('Benchmarks')

import util.util
import util as util

def add_to_reservation():
    try:
        with open(os.devnull, "w") as fnull:
            out = subprocess.check_output(["mrsvctl -m -a CLASS==janus-admin benchmark-*"] , shell=True,stderr = fnull)
    except:
        logger.error("Cannot find reservations: benchmark-*")
    try:
        with open(os.devnull, "w") as fnull:
            out = subprocess.check_output(["mrsvctl -m -a CLASS==janus-admin PM-*"] , shell=True, stderr = fnull)
    except:
        logger.error("Cannot find reservations: PM-*")


def reservation_list(x):
    try:
        with open(os.devnull, "w") as fnull:
            p1 = subprocess.Popen(['showres','-g','-n',x], stdout=subprocess.PIPE,stderr = fnull)
            p2 = subprocess.Popen(['cut', '-d',' ', '-f','1'], stdin=p1.stdout, stdout=subprocess.PIPE,stderr = fnull)
            p1.stdout.close()
        output = p2.communicate()[0]
        nodes = []
        for n in output.split():
            if n.startswith('node') and n[-4:].isdigit():
                nodes.append(n)
        return nodes
    except:
        logger.error("Issues with reservation "+x)

def reservations():

    reserved_nodes = []
    p1 = subprocess.Popen(['scontrol','-o', 'show','res'], stdout=subprocess.PIPE)
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

    # reservations = {}
    # #showres | cut -d' ' -f1 | uniq | sort
    # p1 = subprocess.Popen(['showres'], stdout=subprocess.PIPE)
    # p2 = subprocess.Popen(['cut', '-d',' ', '-f','1'], stdin=p1.stdout, stdout=subprocess.PIPE)
    # p1.stdout.close()
    # output = p2.communicate()[0]
    #
    # for x in output.split():
    #     if x and x[0].isalpha() and x[-1].isdigit():
    #         if (x.startswith('janus-debug') or
    #             x.startswith('wide') or
    #             x.startswith('PM') or
    #             x.startswith('small')):
    #             pass
    #         else:
    #             nodes = reservation_list(x)
    #             reservations[x] = len(nodes)
    #             reserved_nodes.extend(nodes)
    #
    logger.info("Total reserved ".ljust(20)+str(len(reserved_nodes)).rjust(5))


    return list(set(reserved_nodes))

def benchmark_nodes():
    reserved_nodes = []
    p1 = subprocess.Popen(['showres'], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['cut', '-d',' ', '-f','1'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    output = p2.communicate()[0]

    for x in output.split():
        if x.startswith('benchmark'):
            nodes = reservation_list(x)
            reserved_nodes.extend(nodes)
    return list(set(reserved_nodes))


def free_PBS_nodes(host_expression):

    nodes_names = expand_hostlist(host_expression)
    node_string = "".join(["%s " % n for n in nodes_names])
    #pbsOut = subprocess.check_output(["pbsnodes -x %s" % node_string] , shell=True)
    pbsOut = subprocess.check_output(["pbsnodes -x"] , shell=True)
    nodes = xml2obj(pbsOut)
    freenodelist = []
    downnodes = []

    # find free nodes: state = free, no jobs are runing, no message
    for node in nodes["Node"]:
        status = {}
        messages = []
        jobs = []
        name = node["name"]
        state = node["state"]
        if state == "free" and name.startswith('node'):
            if node["jobs"]:
                # node has a job running
                jobs = node["jobs"].split(", ")
                continue
            if "status" in node:
                for item in node["status"].split(","):
                    try:

                        S, value = item.split("=")
                        status[S] = value
                        #print 'good', S, value
                    except ValueError:
                        pass
                if status.has_key("message"):
                    continue
            #print name
            freenodelist.append(name)
    logger.info("Free nodes".ljust(20)+str(len(freenodelist)).rjust(5))
    return freenodelist

def free_SLURM_nodes(nodelist):
    node_list = expand_hostlist(nodelist)
    #print len(node_list)

    p1 = subprocess.Popen(['scontrol','-o', 'show','nodes'], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['grep', 'Reason'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    out, err = p2.communicate()

    not_available_nodes = re.findall(r'NodeName=(node[0-9]+)', out)

    diff_set = set(node_list).difference(set(not_available_nodes))
    logger.info("Free nodes".ljust(20)+str(len(diff_set)).rjust(5))
    return diff_set

def execute(directory,  list, exclude, reservation):

    logger.info(directory)

    logger.info('createing node list')
    free_nodes = free_SLURM_nodes("node[01-17][01-80]")
    reserved_nodes = reservations()

    diff_set = set(free_nodes).difference(set(reserved_nodes))
    node_list = []
    for node in diff_set:
        node_list.append(node)
    # if not list:
    #     # else:
    #     reserved_nodes = reservations()
    #     if reservation:
    #         resnodes = reservation_list(reservation)
    #         # print len(resnodes), type(resnodes)
    #         # print len(reserved_nodes), type(reserved_nodes)
    #         tmp = set(reserved_nodes).difference(set(resnodes))
    #         reserved_nodes = []
    #         for n in tmp:
    #             reserved_nodes.append(n)
    #         # print len(reserved_nodes)
    #         #reserved_nodes = list(set(reserved_nodes).difference(set(resnodes)))
    #         #print len(reserved_nodes)
    #
    #     free_nodes = free_PBS_nodes("node[01-17][01-80]")
    #
    #     free_janus_nodes = []
    #     for n in free_nodes:
    #         if n.startswith('node') and n[-4:].isdigit():
    #             free_janus_nodes.append(n)
    #
    #     diff_set = set(free_janus_nodes).difference(set(reserved_nodes))
    #
    #     if reservation:
    #         for n in diff_set:
    #             if n in resnodes:
    #                 node_list.append(n)
    #     else:
    #         for n in diff_set:
    #             node_list.append(n)
    #     logger.info("Node list".ljust(20)+str(len(node_list)).rjust(5))
    #
    #
    # else:
    #     node_list_tmp = util.read_node_list(list)
    #
    #     logger.info("Node list given".ljust(20)+str(len(node_list_tmp)).rjust(5))
    #     free_nodes = free_PBS_nodes("node[01-17][01-80]")
    #     free_janus_nodes = []
    #     for n in free_nodes:
    #         if n.startswith('node') and n[-4:].isdigit():
    #             free_janus_nodes.append(n)
    #
    #     not_free_list = []
    #     for n in node_list_tmp:
    #         if n in free_janus_nodes:
    #             node_list.append(n)
    #         else:
    #             not_free_list.append(n)
    #     logger.info("Node list not free".ljust(20)+str(len(not_free_list)).rjust(5))
    #     logger.info("Node list".ljust(20)+str(len(node_list)).rjust(5))
    #
    #
    # if exclude:
    #
    #     try:
    #         exclude_list = expand_hostlist(exclude)
    #         logger.info("excluding nodes".ljust(20)+str(len(exclude_list)).rjust(5))
    #         diff_set = set(node_list).difference(set(exclude_list))
    #         logger.info("".ljust(5)+"difference".ljust(15)+str(len(node_list) - len(diff_set)).rjust(5))
    #         node_list = []
    #         for n in diff_set:
    #             node_list.append(n)
    #     except:
    #         logger.error("Cannot create exclude list")
    #
    logger.info("Available nodes".ljust(20)+str(len(node_list)).rjust(5))
    #
    #
    # # # add janus-admin to reservation
    # # add_to_reservation()
    #
    #
    #Write list to file
    try:
        f = open(os.path.join(directory,'node_list'), 'w')
        for item in node_list:
          f.write("%s\n" % item)
        f.close()
    except:
        logger.error("create: ".rjust(20)+"could not write node_list to file")
