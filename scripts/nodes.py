#!/usr/bin/env python

from util.hostlist import expand_hostlist
from util.xml2obj import xml2obj
import subprocess
import logging
import os

logger = logging.getLogger('Benchmarks')

def reservation_list(x):
    #try:
    with open(os.devnull, "w") as fnull:
        p1 = subprocess.Popen(['showres','-g','-n',x], stdout=subprocess.PIPE,stderr = fnull)
        p2 = subprocess.Popen(['cut', '-d',' ', '-f','1'], stdin=p1.stdout, stdout=subprocess.PIPE,stderr = fnull)
        p1.stdout.close()
    output = p2.communicate()[0]
    #print output
    nodes = []
    for n in output.split():
        #print n
        if n.startswith('node') and n[-4:].isdigit():
            nodes.append(n)
    return nodes
    #except:
    #    logger.error("Issues with reservation "+x)

def reserved_nodes(node_list):

    #showres | cut -d' ' -f1 | uniq | sort
    p1 = subprocess.Popen(['showres'], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['cut', '-d',' ', '-f','1'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    output = p2.communicate()[0]

    for x in output.split():
        if x and x[0].isalpha() and x[-1].isdigit():
            if (x.startswith('janus-debug') or
                x.startswith('wide') or
                x.startswith('PM') or
                #x.startswith('benchmark') or
                x.startswith('small')):
                pass
            else:
                nodes = reservation_list(x)
                print x
                if nodes:
                    for n in nodes:
                        node_list[n].append('res='+x)

    return node_list

def pbs_nodes(node_list):

    pbsOut = subprocess.check_output(["pbsnodes -x"] , shell=True)
    nodes = xml2obj(pbsOut)

    # find free nodes: state = free, no jobs are runing, no message
    for node in nodes["Node"]:
        status = {}
        messages = []
        jobs = []

        name = node["name"]
        state = node["state"]

        if name in node_list:
            node_list[name].append(state)
            #print name, state
            if state == 'free':

                if node["jobs"]:
                    # node has a job running
                    node_list[name].append('job running')
                    continue
                if "status" in node:
                    for item in node["status"].split(","):
                        (S, value) = item.split("=")
                        status[S] = value
                    if status.has_key("message"):

                        node_list[name].append('message: '+status['message'])
    return node_list

def execute():

    all_janus_nodes = expand_hostlist('node[01-17][01-80]')
    logger.info("janus nodes".ljust(20)+str(len(all_janus_nodes)).rjust(5))

    # Create initial dictionary
    node_list = {}
    for n in all_janus_nodes:
        node_list[n] = []

    # find all nodes that are reserved
    node_list = pbs_nodes(node_list)
    node_list = reserved_nodes(node_list)


    for x,y in node_list.iteritems():
        # if 'job-exclusive' in node_list[x]:
        #     continue
        # if 'free' in node_list[x] and 'job running' in node_list[x]:
        print x, node_list[x]
