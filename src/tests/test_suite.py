"""Automated test suite for curc-bench"""
import unittest
import re


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
        
        

if __name__ == '__main__':
    unittest.main()
