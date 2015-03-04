"""Automated test suite for curc-bench"""
import unittest
import re
import pyslurm
import os
import subprocess

from bench.util.hostlist import expand_hostlist

def slurm_setup():
    """Loads results from old subprocess.Popen implementation"""
    with open('nodeInfo', 'r') as node_file:
        node_info = node_file.read()
    with open('freeNodeList', 'r') as free_node_file:
        free_nodes = free_node_file.read()
        free_nodes = free_nodes.splitlines()
    return node_info, free_nodes

class MyTest(unittest.TestCase):
    """Test cases for curc-bench"""
    def test(self):
        """An unimportant test"""
        self.assertEqual(1, 1)

    def test_free_SLURM_nodes(self):
        """Test the functionalisty of pyslurm compared to subprocess.Popen commands"""
        # node_info is the result of the following command on a login node:
            #scontrol -o show nodes | grep Reason
        # free_nodes is the result of:
            # grep -o -E "NodeName=(node[0-9]+)" nodeInfo > nodelist
            # grep -o -E "(node[0-9]+)" nodelist > freeNodeList
        node_info, free_nodes = slurm_setup()
        nodes = re.findall(r'NodeName=(node[0-9]+)', node_info)
        #Test that the lists of freenodes match
        self.assertEqual(nodes, free_nodes)

        #TODO: test that pyslurm functionality matches the above functionality

        
        node_list = expand_hostlist("node[01-17][01-80]")
        p1 = subprocess.Popen(['scontrol', '-o', 'show', 'nodes'], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(['grep', 'Reason'], stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()
        out, err = p2.communicate()

        not_available_nodes = re.findall(r'NodeName=(node[0-9]+)', out)

        diff_set = set(node_list).difference(set(not_available_nodes))
        for nn in diff_set:
            print nn




        a = pyslurm.node()
        node_dict = a.get()

        #if len(node_dict) > 0:
        ii = 0
        print "-" * 80
        for key, value in node_dict.iteritems():
	        if ii>3:
		        break
	        ii+=1
            print "%s :" % (key)
            for part_key in sorted(value.iterkeys()):
                #print "\t%-15s : %s" % (part_key, value[part_key])
                if part_key == 'node_hostname':
                    print "    node_hostname = ",value[part_key]
                elif part_key == 'node_state':
                    print "    node_state = ",value[part_key]
                elif part_key == 'reason':
                    print "    reason = ", value[part_key]
                #else:
                #    print "key = ",part_key
            print "-" * 80

        #else:
        #    print "No Nodes found !"
        

if __name__ == '__main__':
    unittest.main()
