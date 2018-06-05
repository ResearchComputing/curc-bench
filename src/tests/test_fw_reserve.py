import bench.framework
import bench.tests.node_test
import bench.tests.bandwidth_test
import bench.tests.alltoall_tests
import bench.tests.ior
import bench.util
import hostlist
import mock
import os
import pkg_resources
import re
import shutil
import tempfile
import unittest
import jinja2

num_nodes = 11


@mock.patch('bench.slurm.scontrol', return_value="Submitted reservation")
class TestReserve(unittest.TestCase):

    def assertIsFile (self, path):
        assert os.path.isfile(path), '{0} does not exist'.format(path)

    def write_files(self, num_nodes=10, pass_range=[], fail_range=[], error_range=[]):
        '''Write files for pass/fail/error nodes where curc bench is
        expecting them. Example: self.write_files(11, [1,5], [6, 9], [10, 11])
        num_nodes = integer
        pass_range = tuple or list with 2 integers
        fail_range = tuple or list with 2 integers
        error_range = tuple or list with 2 integers'''

        self.num_nodes = num_nodes
        self.nodes = ['tnode01{0:02}'.format(i) for i in range(1, self.num_nodes)]

        self.pass_node_range = pass_range
        self.fail_node_range = fail_range
        self.error_node_range = error_range
        self.pass_nodes = []
        self.fail_nodes = []
        self.error_nodes = []

        if self.pass_node_range:
            self.pass_nodes = ['tnode01{0:02}'.format(i) for i in range(self.pass_node_range[0], self.pass_node_range[1] + 1)]
        if self.fail_node_range:
            self.fail_nodes = ['tnode01{0:02}'.format(i) for i in range(self.fail_node_range[0], self.fail_node_range[1] + 1)]
        if self.error_node_range:
            self.error_nodes = ['tnode01{0:02}'.format(i) for i in range(self.error_node_range[0], self.error_node_range[1] + 1)]

        bench.util.write_node_list(os.path.join(self.node_dir, 'pass_nodes'), self.pass_nodes)
        bench.util.write_node_list(os.path.join(self.node_dir, 'fail_nodes'), self.fail_nodes)
        bench.util.write_node_list(os.path.join(self.node_dir, 'error_nodes'), self.error_nodes)
        bench.util.write_node_list(os.path.join(self.directory, 'node_list'), self.nodes)
        bench.util.write_node_list(os.path.join(self.node_dir, 'node_list'), self.nodes)

    def setUp (self):
        self.directory = tempfile.mkdtemp()
        self.node_dir = os.path.join(self.directory, 'node')
        self.node_test_dir = os.path.join(self.node_dir, 'tests')

        os.mkdir(self.node_dir)
        os.mkdir(self.node_test_dir)


    def tearDown (self):
        shutil.rmtree(self.directory)

    def test_reserve(self, arg1):
        '''Test that fail and error nodes are reserved, and that
        pass nodes are not reserved'''

        self.write_files(11, [1,5], [6, 9], [10, 11])

        node_test = bench.tests.node_test.NodeTest("node")
        node_test.Reserve.execute(self.directory)

        args, kwargs = arg1.call_args_list[0]

        self.assertEqual(args[0], 'create')

        for node in self.pass_nodes:
            self.assertNotIn(node, kwargs['nodes'])
        for node in self.fail_nodes:
            self.assertIn(node, kwargs['nodes'])
        for node in self.error_nodes:
            self.assertIn(node, kwargs['nodes'])


    def test_reserve_empty(self, arg1):
        '''Test that an empty reservation isn't created when
        no fail or error nodes exist'''

        self.write_files(11, [1,11])

        node_test = bench.tests.node_test.NodeTest("node")
        node_test.Reserve.execute(self.directory)

        assert not bench.slurm.scontrol.called

























#
