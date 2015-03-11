"""Automated test suite for curc-bench"""
import unittest
import re
import pyslurm
import os
import subprocess

from create import free_SLURM_nodes
from create import reservations
from hostlist import expand_hostlist


class Test_Create(unittest.TestCase):
    """Test cases for curc-bench"""
    def test(self):
        """An unimportant test"""
        self.assertEqual(1, 1)

    def test_create_execute(self):
        """Test the functionalisty of pyslurm compared to subprocess.Popen commands
        in create.py"""

        #Old code using subprocess.Popen
        old_all_nodes = expand_hostlist("node[01-17][01-80]")
        free_nodes = free_SLURM_nodes("node[01-17][01-80]")
        reserved_nodes = reservations()

        diff_set = set(free_nodes).difference(set(reserved_nodes))
        node_list = []
        for node in diff_set:
            node_list.append(node)

        #New code using pyslurm
        #Add all 'IDLE' and 'ALLOCATED' and 'COMPLETING' nodes to list
        a = pyslurm.node()
        node_dict = a.get()
        slurm_free_nodes = set([])
        all_nodes = []

        for key, value in node_dict.iteritems():
            if key[0:4] == 'node': 
                all_nodes.append(key)
            #print "%s :" % (key)
            #if key == 'node0149' or key == 'node1428':
               # print ''
            for part_key in sorted(value.iterkeys()):
                #if key == 'node0903' or key == 'node0805':
                    #print "\t%-15s : %s" % (part_key, value[part_key])
                #print "\t%-15s : %s" % (part_key, value[part_key])
                if part_key == 'node_state':
                    #print "%s :" % (key), "    node_state = ",value[part_key]
                    if (value[part_key] == 'IDLE' or value[part_key] == 'ALLOCATED' or
                                                     value[part_key] == 'COMPLETING'):
                        if key[0:4] == 'node':
                            if int(key[4:6])>=01 and int(key[4:6])<=17:
                                if int(key[6:8])>=01 and int(key[6:8])<=80:
                                    slurm_free_nodes.add(key)
        
        #Remove reserved nodes from slurm_free_nodes list
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
                        if value[part_key][0:4] == 'node':
                            nodes = expand_hostlist(value[part_key])
                            for node in nodes:
                                slurm_reserve_nodes.add(node)
        
        #print ''
        #print "Reserved nodes = ", len(slurm_reserve_nodes)
        
        slurm_free_nodes = slurm_free_nodes.difference(slurm_reserve_nodes)

        #print "Old total nodes found = ", len(old_all_nodes)        
        #print "Free nodes in old code = ", len(node_list)
        #print "Total nodes found = ", len(all_nodes)                            
        #print "Number of slurm free nodes = ",len(slurm_free_nodes)
        
        diff_set = set(slurm_free_nodes).symmetric_difference(set(node_list))
        #print "diff_list = ",list(diff_set)[0:50]
        
        self.assertEqual(len(old_all_nodes),len(all_nodes))
        self.assertEqual(len(node_list), len(slurm_free_nodes))
        self.assertEqual(set(node_list), set(slurm_free_nodes))
        
    def test_create_reservations(self):
        """Test the funcionality of create.reservations when using pyslurm
        instead of subprocess.Popen"""

        #Old code using Popen
        reserved_nodes = set(reservations())

        #New pyslurm
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

        diff_set = reserved_nodes.symmetric_difference(slurm_reserve_nodes)
        #print diff_set

        self.assertEqual(reserved_nodes,slurm_reserve_nodes)


    def test_create_free_SLURM_nodes(self):
        """Test the funcionality of create.free_SLURM_nodes when using pyslurm
        instead of subprocess.Popen"""
        
        #Old code using Popen
        free_nodes = set(free_SLURM_nodes("node[01-17][01-80]"))
        
        #New pyslurm
        a = pyslurm.node()
        node_dict = a.get()
        slurm_free_nodes = set([])
       
        for key, value in node_dict.iteritems():
                          #print "%s :" % (key)
            #if key == 'node0149' or key == 'node1428':
               # print ''
            for part_key in sorted(value.iterkeys()):
                #if key == 'node0903' or key == 'node0805':
                    #print "\t%-15s : %s" % (part_key, value[part_key])
                #print "\t%-15s : %s" % (part_key, value[part_key])
                #if part_key == 'reason':
                    #print value[part_key]
                    #if str(value[part_key]) != 'None':
                        #print "%s :" % (key), "    reason = ",value[part_key]
                if part_key == 'node_state':
                    #print "%s :" % (key), "    node_state = ",value[part_key]
                    if (value[part_key] == 'IDLE' or value[part_key] == 'ALLOCATED' or
                          value[part_key] == 'COMPLETING' or value[part_key] == 'RESERVED'):
                        if key[0:4] == 'node':
                            if int(key[4:6])>=01 and int(key[4:6])<=17:
                                if int(key[6:8])>=01 and int(key[6:8])<=80:
                                    slurm_free_nodes.add(key)

        diff_set = free_nodes.symmetric_difference(slurm_free_nodes)
        #print "sym = ", diff_set

        diff_set = free_nodes.difference(slurm_free_nodes)
        #print "old-new = ", diff_set

        diff_set1 = slurm_free_nodes.difference(free_nodes)
        #print "new-old = ", diff_set1

        #for key, value in node_dict.iteritems():
            #if key in diff_set:
                #for part_key in sorted(value.iterkeys()):
                   #print "\t%-15s : %s" % (part_key, value[part_key])
                   #print "\t%-15s : %s" % (part_key, value[part_key])
        
        self.assertEqual(free_nodes, slurm_free_nodes)


if __name__ == '__main__':
    unittest.main()
