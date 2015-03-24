import os
import subprocess
import datetime
import shutil
import textwrap

from hostlist import expand_hostlist
from util.xml2obj import xml2obj

import logging
logger = logging.getLogger('Benchmarks')

import util.util
from bench.util import util as util

def add_to_reservation():
    try:
        with open(os.devnull, "w") as fnull:
            out = subprocess.check_output(["mrsvctl -m -a CLASS==janus-admin benchmark-*"] , shell=True,stderr = fnull)
            out = subprocess.check_output(["mrsvctl -m -a CLASS==janus-admin PM-*"] , shell=True, stderr = fnull)
    except:
        logger.error("Cannot find reservations: benchmark-* or PM-*")
        pass

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
                x.startswith('benchmark') or    
                x.startswith('small')):
                pass
            else:
                nodes = reservation_list(x)
                reserved_nodes.extend(nodes)
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
                    (S, value) = item.split("=")
                    status[S] = value
                if status.has_key("message"):
                    continue    
            #print name
            freenodelist.append(name)
    logger.info("number of free nodes = " + str(len(freenodelist)))       
    return freenodelist
    
    
def execute(directory, retest, list, exclude):
       
    logger.info(directory)
    
    node_list = []
    if not list:
    
        #Create a node list
        if retest:
            node_list = benchmark_nodes()
            reserved_nodes = reservations()
            diff_set = set(node_list).difference(set(reserved_nodes)) 
            for n in diff_set:
                node_list.append(n)
            
            logger.info("Benchmark-* nodes".ljust(20)+str(len(node_list)).rjust(5))

        else:
            reserved_nodes = reservations()
            free_nodes = free_PBS_nodes("node[01-17][01-80]")
            free_janus_nodes = []
            for n in free_nodes:
                if n.startswith('node') and n[-4:].isdigit():
                    free_janus_nodes.append(n)
     
            diff_set = set(free_janus_nodes).difference(set(reserved_nodes)) 
            for n in diff_set:
                node_list.append(n)
            logger.info("Reserved nodes".ljust(20)+str(len(reserved_nodes)).rjust(5))
            logger.info("Free nodes".ljust(20)+str(len(free_nodes)).rjust(5))
                
    else:
        node_list = util.read_node_list(list)    
        logger.info("Node list".ljust(20)+str(len(node_list)).rjust(5))
        

    if exclude:

        try:
            exclude_list = expand_hostlist(exclude)
            logger.info("excluding nodes".ljust(20)+str(len(exclude_list)).rjust(5))   
            diff_set = set(node_list).difference(set(exclude_list))
            node_list = []
            for n in diff_set:
                
                
                node_list.append(n)
        except:
            logger.error("Cannot create exclude list")
    
    logger.info("Available nodes".ljust(20)+str(len(node_list)).rjust(5))   
    
    
    # add janus-admin to reservation
    add_to_reservation()
    
    #Write list to file
    try:
        f = open(os.path.join(directory,'node_list'), 'w')
        for item in node_list:
          f.write("%s\n" % item)
        f.close()
    except:
        logger.error("create: ".rjust(20)+"could not write node_list to file")
    
    
    
    
    
    
    
