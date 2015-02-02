#!/usr/bin/env python

import os
import subprocess

import import_tests.import_nodes as import_nodes
import import_tests.import_bandwidth as import_bandwidth

from bench.import_tests import import_alltoall2 as import_alltoall
from bench.import_tests import import_hpl as import_hpl
from bench.util import util as util

from util.hostlist import expand_hostlist

import logging
logger = logging.getLogger('Benchmarks')

def write_to_file(directory,name, data):
    f = open(os.path.join(directory,name), 'w')
    for item in data['bad_nodes']:
        f.write("%s\n" % item)
    f.close()
    
def write_all_to_file(directory,name, data):
    
    # Bad nodes
    filename = name+'_bad_nodes'
    f = open(os.path.join(directory,filename), 'w')
    for item in data['bad_nodes']:
        f.write("%s\n" % item)
    f.close()    
    
    # Bad nodes + not tested
    filename = name+'_bad_not_tested_nodes'
    not_bad = set(data['bad_nodes']).union(set(data['not_tested']))
    f = open(os.path.join(directory,filename), 'w')
    for item in not_bad:
        f.write("%s\n" % item)
    f.close()
    
    # good nodes
    filename = name+'_good_nodes'
    f = open(os.path.join(directory,filename), 'w')
    for item in data['good_nodes']:
        f.write("%s\n" % item)
    f.close()
    
def summary(data):
    logger.info("Bad nodes  = "+str(len(data['bad_nodes'])))
    logger.info("Good nodes = "+str(len(data['good_nodes'])))
    logger.info("Not tested = "+str(len(data['not_tested'])))
    logger.info("Total      = "+str(len(data['good_nodes'])+len(data['bad_nodes'])+len(data['not_tested'])))

def not_tested(all_janus_nodes, directory, node_list, total_not_tested, total_bad_nodes):
    tmp = set(total_bad_nodes).union(
                           set(total_not_tested))                   
                           
    total_good_nodes = set(node_list).difference(tmp)     
    
    logger.info("")
    logger.info("Total not tested = "+str(len(total_not_tested)))
    logger.info("Total bad nodes  = "+str(len(total_bad_nodes)))
    logger.info("Total good nodes  = "+str(len(total_good_nodes)))
    
    data = {}
    data['bad_nodes'] = total_not_tested
    write_to_file(directory, 'not_tested', data)
    data['bad_nodes'] = total_bad_nodes
    write_to_file(directory, 'bad_nodes', data)
    
    not_in_test = (set(all_janus_nodes).difference(total_bad_nodes.union(total_good_nodes).union(total_not_tested)))
    logger.info("Total not in test  = "+str(len(not_in_test)))
    data['bad_nodes'] = not_in_test
    write_to_file(directory, 'not_in_test', data)




def execute(directory, args):
    
    all_janus_nodes = expand_hostlist('node[01-17][01-80]')
    
    logger.info(directory)
    
    node_list = util.read_node_list(os.path.join(directory,'node_list'))    
    logger.info("Node list".ljust(20)+str(len(node_list)).rjust(5))
    
    if not args.allrack and not args.allswitch and not args.bandwidth and not args.nodes and not args.allpair:
        
        # Node level
        node = import_nodes.execute(directory,node_list)
        summary(node)
        write_all_to_file(directory, 'list_node',node)
        
        # Bandwidth level
        band = import_bandwidth.execute(directory, node_list)
        summary(band)
        write_all_to_file(directory, 'list_band',band)
        
        # Alltoall rack
        allto = import_alltoall.execute_rack(directory, node_list)
        summary(allto)
        write_all_to_file(directory, 'list_all_rack',allto)
        
        # Alltoall rack-switch
        allto_s = import_alltoall.execute_switch(directory, node_list)
        summary(allto_s)
        write_all_to_file(directory, 'list_all_switch',allto_s)
        
        # Alltoall pair
        allto_p = import_alltoall.execute_pair(directory, node_list)
        summary(allto_p)
        write_all_to_file(directory, 'list_all_pair',allto_p)
        
        
        total_not_tested = set(allto['not_tested']).union(
                           set(allto_s['not_tested'])).union(
                           set(allto_p['not_tested'])).union(
                           set(band['not_tested'])).union(
                           set(node['not_tested']))
                               
        total_bad_nodes = set(allto['bad_nodes']).union(
                           set(allto_s['bad_nodes'])).union(
                           set(allto_p['bad_nodes'])).union(
                           set(band['bad_nodes'])).union(
                           set(node['bad_nodes']))
                           
        not_tested(all_janus_nodes, directory, node_list,total_not_tested,total_bad_nodes)
    
    else:
             
        if args.allrack==True:
           # Alltoall rack
           allto = import_alltoall.execute_rack(directory, node_list)
           summary(allto)
           write_all_to_file(directory, 'list_all_rack',allto)
        
        if args.allswitch==True:
           # Alltoall rack-switch
           allto_s = import_alltoall.execute_switch(directory, node_list)
           summary(allto_s)
           write_all_to_file(directory, 'list_all_switch',allto_s)
        
        if args.allpair==True:
           # Alltoall pair
           allto_p = import_alltoall.execute_pair(directory, node_list)
           summary(allto_p)
           write_all_to_file(directory, 'list_all_pair',allto_p)
           
        if args.bandwidth==True:
            band = import_bandwidth.execute(directory, node_list)
            summary(band)
            write_to_file(directory, 'list_band',band)
            
        if args.nodes==True:
            node = import_nodes.execute(directory,node_list)
            summary(node)
            write_to_file(directory, 'list_node',node)

            total_not_tested = set(node['not_tested'])
            total_bad_nodes = set(node['bad_nodes'])
                           
            not_tested(all_janus_nodes, directory, node_list,total_not_tested,total_bad_nodes)
  
    

    
    
    
    
    
    
    
    
    
    
    