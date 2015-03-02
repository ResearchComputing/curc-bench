#Automated test suite for curc-bench
import unittest
import re


def slurmNodesSetup():

    with open('nodeInfo', 'r') as f:
    	nodeInfo = f.read()
    with open('freeNodeList', 'r') as f:
    	freeNodes = f.read()
    	freeNodes = freeNodes.splitlines()
    return nodeInfo, freeNodes

#Trying to get automated tests to run
def unimportantTest():
	return 1

class MyTest(unittest.TestCase):
    def test(self):
        self.assertEqual(unimportantTest(), 1)

    def test_slurmFreeNodes(self):
    	#test the functionalisty of pyslurm compared to subprocess Popen commands
    	# nodeInfo is the result of the following command on a login node:
	    	#scontrol -o show nodes | grep Reason
	   	# freeNodes is the result of:
	   		# grep -o -E "NodeName=(node[0-9]+)" nodeInfo > nodelist
	   		# grep -o -E "(node[0-9]+)" nodelist > freeNodeList

    	nodeInfo, freeNodes = slurmNodesSetup()
    	nodes = re.findall(r'NodeName=(node[0-9]+)', nodeInfo)
    	#Test that the lists of freenodes match
    	self.assertEqual(nodes,freeNodes)

    	#TODO: test pyslurm functionality matches the above functionality

if __name__ == '__main__':
    unittest.main()