#!/usr/bin/env python

import os
import subprocess
import re

from bench.util.hostlist import expand_hostlist
from bench.util.xml2obj import xml2obj

import logging
logger = logging.getLogger('Benchmarks')


def add_to_reservation():
    try:
        with open(os.devnull, "w") as fnull:
            out = subprocess.check_output(["mrsvctl -m -a CLASS==janus-admin benchmark-*"], \
                shell=True, stderr=fnull)
    except:
        logger.error("Cannot find reservations: benchmark-*")
    try:
        with open(os.devnull, "w") as fnull:
            out = subprocess.check_output(["mrsvctl -m -a CLASS==janus-admin PM-*"], \
                shell=True, stderr=fnull)
    except:
        logger.error("Cannot find reservations: PM-*")


def reservation_list(x):
    try:
        with open(os.devnull, "w") as fnull:
            p1 = subprocess.Popen(['showres', '-g', '-n', x], stdout=subprocess.PIPE, stderr=fnull)
            p2 = subprocess.Popen(['cut', '-d', ' ', '-f', '1'], stdin=p1.stdout, \
                stdout=subprocess.PIPE, stderr=fnull)
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

def benchmark_nodes():
    reserved_nodes = []
    p1 = subprocess.Popen(['showres'], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['cut', '-d', ' ', '-f', '1'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    output = p2.communicate()[0]

    for x in output.split():
        if x.startswith('benchmark'):
            nodes = reservation_list(x)
            reserved_nodes.extend(nodes)
    return list(set(reserved_nodes))


def free_PBS_nodes(host_expression):

    nodes_names = expand_hostlist(host_expression)
    pbsOut = subprocess.check_output(["pbsnodes -x"], shell=True)
    nodes = xml2obj(pbsOut)
    freenodelist = []

    # find free nodes: state = free, no jobs are runing, no message
    for node in nodes["Node"]:
        status = {}
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
