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


class TestReserve(unittest.TestCase):

    scontrol_show_return_1=['''ReservationName=bench-node StartTime=2018-05-02T16:35:14 EndTime=2019-05-02T16:35:14 Duration=365-00:00:00
     Nodes=node[0325-0328] NodeCnt=4 CoreCnt=96 Features=(null) PartitionName=(null) Flags=OVERLAP,SPEC_NODES
     TRES=cpu=96
     Users=asdf1,asdf2,asdf3 Accounts=(null)
     Licenses=(null) State=ACTIVE BurstBuffer=(null) Watts=n/a''',
     'Scontrol create called']

    scontrol_show_return_2=['Reservation bench-node not found', 'Scontrol create called']

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

    @mock.patch('bench.slurm.scontrol', return_value="Scontrol called")
    def test_reserve(self, arg1):
        '''Test that fail and error nodes are reserved, and that
        pass nodes are not reserved'''

        self.write_files(11, [1,5], [6, 9], [10, 11])

        node_test = bench.tests.node_test.NodeTest("node")
        node_test.Reserve.execute(self.directory)

        #scontrol show ReservationName= checks for existing
        args_0, kwargs_0 = arg1.call_args_list[0]
        #scontrol create makes a reservation
        args_1, kwargs_1 = arg1.call_args_list[1]

        self.assertEqual(kwargs_0['subcommand'], 'show')
        self.assertEqual(kwargs_1['subcommand'], 'create')

        for node in self.pass_nodes:
            self.assertNotIn(node, kwargs_1['nodes'])
        for node in self.fail_nodes:
            self.assertIn(node, kwargs_1['nodes'])
        for node in self.error_nodes:
            self.assertIn(node, kwargs_1['nodes'])


    @mock.patch('bench.slurm.scontrol', return_value="Scontrol called")
    def test_reserve_empty(self, arg1):
        '''Test that an empty reservation isn't created when
        no fail or error nodes exist'''

        self.write_files(11, [1,11])

        node_test = bench.tests.node_test.NodeTest("node")
        node_test.Reserve.execute(self.directory)

        assert not bench.slurm.scontrol.called


    @mock.patch('bench.slurm.scontrol', side_effect=scontrol_show_return_1)
    # @mock.patch('bench.slurm.scontrol', return_value="Scontrol called")
    def test_reserve_already_exists(self, arg1):
        '''Test that a reservation is recreated/updated if
        reserve is called again'''

        self.write_files(11, [1,5], [6, 9], [10, 11])

        node_test = bench.tests.node_test.NodeTest("node")
        node_test.Reserve.execute(self.directory)

        #scontrol show ReservationName= checks for existing
        args_0, kwargs_0 = arg1.call_args_list[0]
        #scontrol create makes a reservation
        args_1, kwargs_1 = arg1.call_args_list[1]

        assert bench.slurm.scontrol.called
        self.assertEqual(kwargs_0['subcommand'], 'show')
        self.assertEqual(kwargs_1['subcommand'], 'update')

        for node in self.pass_nodes:
            self.assertNotIn(node, kwargs_1['nodes'])
        for node in self.fail_nodes:
            self.assertIn(node, kwargs_1['nodes'])
        for node in self.error_nodes:
            self.assertIn(node, kwargs_1['nodes'])



















#
