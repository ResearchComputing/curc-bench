#!/usr/bin/env python
import subprocess
import getpass
import xml.etree.ElementTree as ET
import re

import logging
logger = logging.getLogger('Benchmarks')

def evaluate():
    
    queues = overview()
    jobs = 0
    for q in queues:
        jobs += int(q.attrib['count'])
    
    if jobs == 0:
        return True
    
    return False


def overview():
    
    user_name = getpass.getuser()
    pbsOut = subprocess.check_output(["showq --xml -u %s" % user_name] , shell=True)
    root = ET.fromstring(pbsOut)
    queues = root.findall("./queue")
    index = 1
    for q in queues:
        logger.info(q.attrib['option'].rjust(18)+ " : "+ q.attrib['count'].rjust(4))
    return queues
    
def checkjob(jobid):
    host_list = []
    pbs_out = subprocess.check_output(["checkjob %s --xml" % jobid] , shell=True)
    root = ET.fromstring(pbs_out)
    for i in root.findall('.'):
        tmp = i[0].attrib['HostList']
        tmp = re.sub('[,]', ':', tmp)
        for n in tmp.split(':'):
            if n.startswith('node'):
                host_list.append(n)
    return host_list
    

def generate_node_state():
    
    nodes_names = expand_hostlist("node[01-17][01-80]")
    node_string = "".join(["%s " % n for n in nodes_names])
    pbs_node_state = subprocess.check_output(["pbsnodes -x %s" % node_string] , shell=True)
    nodes = ET.fromstring(pbs_node_state)
    
    node_state ={}
    
    for n in nodes.findall("Node"):
        
        node_state[n.find('name').text] = {}
        node_state[n.find('name').text]['state'] = n.find('state').text
        job_ids = []
        try:
            for j in n.find('jobs').text.split():
                job_ids.append(j.split('/')[1].split('.')[0])
        except:
            pass
        try:
            j_list = n.find('status').text.split()[0]
            tmp = j_list.split(',')[7].split('=')[1]
            print n.find('name').text, tmp
                #job_ids.append(j.split('/')[1].split('.')[0])
        except:
            pass    
            
            
        node_state[n.find('name').text]['jobids'] = set(job_ids)
        node_state[n.find('name').text]['job_num'] = len(job_ids)
        node_state[n.find('name').text]['needed'] = 12
        node_state[n.find('name').text]['load'] = 1
        
        
        
    return node_state

def check_nodes(job_list, node_state):
    
    job_state = []
    job_load = []
    job_num = []
    
    for node in job_list:
        job_state.append(node_state[node]['state'])
        job_load.append(node_state[node]['load'])
        job_num.append(node_state[node]['job_num'])
    
    if 'job-exclusive' in job_state:
        print "job-exclusive".rjust(20),
    elif 'down' in job_state:
        print "down".rjust(20),
    elif 'free' in job_state:
        print 'free'.rjust(20),
    else:
        print 'unknown'.rjust(20),
    
    mean_load = sum(job_load)
    mean_num_jobs = sum(job_num)
    
    print str(mean_load).rjust(20), 
    
    print str(mean_num_jobs).rjust(20),
        
        
        
     
def detailed(queue):
    
    node_state = generate_node_state()
    
    index = 1
    for q in queue:   
        if q.attrib['option'] == 'eligible' or q.attrib['option'] == 'blocked':
            for j in q:
                print j.attrib['JobID'].rjust(10),
                print j.attrib['State'].rjust(10),
                #print j.attrib['JobName']
                #print j.attrib
                if index < 100:
                    node_list = checkjob(j.attrib['JobID'])
                    check_nodes(node_list, node_state)
                    
                    index+=1
                print ""
                    
                    
def execute(verbose):
    
    q = overview() 
    
    if verbose:
        detailed(q)


