"""Automated test suite for curc-bench"""
import unittest
import re
import pyslurm
import os
import subprocess

from create import free_SLURM_nodes
from create import reservations
from hostlist import expand_hostlist


class MyTest(unittest.TestCase):
    """Test cases for curc-bench"""
    def test(self):
        """An unimportant test"""
        self.assertEqual(1, 1)

    def test_free_SLURM_nodes(self):
        """Test the functionalisty of pyslurm compared to subprocess.Popen commands"""

        #TODO: test that pyslurm functionality matches old functionality
        free_nodes = free_SLURM_nodes("node[01-17][01-80]")
        reserved_nodes = reservations()

        diff_set = set(free_nodes).difference(set(reserved_nodes))
        node_list = []
        for node in diff_set:
            node_list.append(node)


        a = pyslurm.node()
        node_dict = a.get()
        slurm_free_nodes=[]
        #if len(node_dict) > 0:
        ii = 0
        print "-" * 80
        for key, value in node_dict.iteritems():
            #if ii > 30:
            #    break
            #ii += 1
            #print "%s :" % (key)
            for part_key in sorted(value.iterkeys()):
                #print "\t%-15s : %s" % (part_key, value[part_key])
                if part_key == 'node_state':
                    #print "%s :" % (key), "    node_state = ",value[part_key]
                    if value[part_key] == 'IDLE':
                        if key[0:4] == 'node':
                            if int(key[4:6])>=01 and int(key[4:6])<=17:
                                if int(key[6:8])>=01 and int(key[6:8])<=80:
                                    slurm_free_nodes.append(key)

        self.assertEqual(node_list, slurm_free_nodes)
                #else:
                #    print "key = ",part_key
            #print "-" * 80

        # #else:
        # #    print "No Nodes found !"
        # print ''
        # print "Number of slurm free nodes = ",len(slurm_free_nodes)
        # #for nn in slurm_free_nodes:
        # #    print nn

if __name__ == '__main__':
    unittest.main()
