import bench.framework
import bench.tests.node_test
import bench.tests.bandwidth_test
import bench.tests.alltoall_tests
import bench.tests.ior
import bench.util
import hostlist
import os
import pkg_resources
import re
import shutil
import tempfile
import unittest
import jinja2
import collections

from unittest import mock



node_script = '''#!/bin/bash
#SBATCH --job-name={{job_name}}
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --nodelist={{node_name}}
#SBATCH --time=0:45:00

STREAM={{stream_path}}
LINPACK={{linpack_path}}


LINPACK_INPUT="\
Sample Intel(R) Optimized LINPACK Benchmark data file (lininput_xeon64)
Intel(R) Optimized LINPACK Benchmark data
6                     # number of tests
1000 5000 10000 20000 25000 150000# problem sizes
1000 5000 10000 20000 25000 150000# leading dimensions
2 2 2 1 1 1  # times to run a test
4 4 4 4 4 4  # alignment values (in KBytes)"


function main
{
    module load intel

    $STREAM >stream.out

    echo >linpack_input "${LINPACK_INPUT}"
    $LINPACK linpack_input >linpack.out
}


main'''

alltoall_script = '''#!/bin/bash
#SBATCH --job-name={{job_name}}
#SBATCH --nodelist={{','.join(nodes)}}
#SBATCH --time=1:30:00
#SBATCH --ntasks-per-node=1
#SBATCH --exclusive

OSU_ALLTOALL={{osu_alltoall_path}}


function main
{
    ml intel/16.0.3
    ml impi/5.1.3.210

    mpirun $OSU_ALLTOALL -f > {{subtest}}.out
}


main'''


@mock.patch('bench.slurm.sbatch', return_value="Submitted batch job")
class TestSubmitNode(unittest.TestCase):

    def assertIsFile (self, path):
        assert os.path.isfile(path), '{0} does not exist'.format(path)

    def setUp (self):
        self.directory = tempfile.mkdtemp()
        self.node_dir = os.path.join(self.directory, 'node')
        self.node_test_dir = os.path.join(self.node_dir, 'tests')
        self.num_nodes = 11

        os.mkdir(self.node_dir)
        os.mkdir(self.node_test_dir)

        self.nodes = ['tnode01{0:02}'.format(i) for i in range(1, self.num_nodes)]
        self.bench_node_list = os.path.join(self.directory, 'node_list')
        bench.util.write_node_list(os.path.join(self.directory, 'node_list'),
                                   self.nodes)
        bench.util.write_node_list(os.path.join(self.node_dir, 'node_list'),
                                   self.nodes)

        self.linpack_path = '/fake/linpack.so'
        self.stream_path = '/fake/stream.so'

        self.TEMPLATE = jinja2.Template(node_script,
            keep_trailing_newline=True)

        for ii in range(0, self.num_nodes - 1):
            script_dir = os.path.join(self.node_test_dir, self.nodes[ii])
            os.makedirs(script_dir)

            script_file = os.path.join(script_dir, self.nodes[ii] + '.job')
            with open(script_file, 'w') as fp:
                fp.write(self.TEMPLATE.render(
                    job_name = 'bench-node-{0}'.format(self.nodes[ii]),
                    node_name = self.nodes[ii],
                    linpack_path = self.linpack_path,
                    stream_path = self.stream_path,
                ))
            bench.util.write_node_list(os.path.join(self.node_test_dir, self.nodes[ii],
                            'node_list'), [self.nodes[ii]])


    def tearDown (self):
        shutil.rmtree(self.directory)


    def test_submit_jobs_1(self, arg1):
        '''Test submit of node jobs with no extra arguments'''
        node_test = bench.tests.node_test.NodeTest("node")
        node_test.Submit.execute(self.directory)#, reservation="fake_res")

        self.assertTrue(bench.slurm.sbatch.called)

        for ii, call in enumerate(arg1.call_args_list):
            script_dir = os.path.join(self.node_test_dir, self.nodes[ii])
            args, kwargs = call #call object is two things: args=tuple, kwargs=dict
            self.assertEqual(kwargs['chdir'], script_dir)
            self.assertEqual(args[0], script_dir + '/' + self.nodes[ii] + '.job')
            self.assertFalse('reservation' in kwargs)

    def test_submit_jobs_2(self, arg1):
        '''Test submit of node jobs with an account, qos, and reservation'''
        node_test = bench.tests.node_test.NodeTest("node")
        node_test.Submit.execute(self.directory, reservation='fake_res',
                    account='fake_account', qos='fake_qos')

        self.assertTrue(bench.slurm.sbatch.called)

        for ii, call in enumerate(arg1.call_args_list):
            script_dir = os.path.join(self.node_test_dir, self.nodes[ii])
            args, kwargs = call #call object is two things: args=tuple, kwargs=dict
            self.assertEqual(kwargs['chdir'], script_dir)
            self.assertEqual(kwargs['reservation'], 'fake_res')
            self.assertEqual(kwargs['account'], 'fake_account')
            self.assertEqual(kwargs['qos'], 'fake_qos')
            self.assertEqual(args[0], script_dir + '/' + self.nodes[ii] + '.job')

    def test_submit_jobs_3(self, arg1):
        '''Test that submit doesn't submit jobs with nodes in --nodelist'''
        node_test = bench.tests.node_test.NodeTest("node")
        node_test.Submit.execute(self.directory, nodelist='tnode01[01-06]')

        self.assertTrue(bench.slurm.sbatch.called)

        for ii, call in enumerate(arg1.call_args_list):
            script_dir = os.path.join(self.node_test_dir, self.nodes[ii])
            args, kwargs = call #call object is two things: args=tuple, kwargs=dict
            self.assertEqual(kwargs['chdir'], script_dir)
            self.assertEqual(args[0], script_dir + '/' + self.nodes[ii] + '.job')
            # Check that --nodelist nodes not submitted
            for node in hostlist.expand_hostlist('tnode01[07-10]'):
                self.assertNotIn(node, kwargs['chdir'])



@mock.patch.dict(bench.conf.alltoall_conf.config, {'osu_a2a_path' : '/fake/osu_alltoall.so'})
@mock.patch.dict(bench.conf.alltoall_conf.config, {'nodes' : 'tnode01[01-20]'})
@mock.patch.dict(bench.conf.alltoall_conf.config, {'Switch': {'switch_1' : 'tnode01[01-05]',
                                                'switch_2' : 'tnode01[06-10]',
                                                'switch_3' : 'tnode01[11-15]',
                                                'switch_4' : 'tnode01[16-20]'}})
@mock.patch('bench.slurm.sbatch', return_value="Submitted batch job")
class TestSubmitSwitch(unittest.TestCase):

    def assertIsFile (self, path):
        assert os.path.isfile(path), '{0} does not exist'.format(path)

    def setUp (self):
        self.directory = tempfile.mkdtemp()
        self.switch_dir = os.path.join(self.directory, 'alltoall-switch')
        self.switch_test_dir = os.path.join(self.switch_dir, 'tests')

        os.mkdir(self.switch_dir)
        os.mkdir(self.switch_test_dir)

        self.nodes = hostlist.expand_hostlist('tnode01[01-20]')
        self.test_name = 'alltoall-switch'

        self.bench_node_list = os.path.join(self.directory, 'node_list')
        bench.util.write_node_list(os.path.join(self.directory, 'node_list'),
                                   self.nodes)
        bench.util.write_node_list(os.path.join(self.switch_dir, 'node_list'),
                                   self.nodes)

        self.alltoall_path = '/fake/alltoall.so'

        self.switches = {}
        self.switches['switch_1'] = hostlist.expand_hostlist('tnode01[01-05]')
        self.switches['switch_2'] = hostlist.expand_hostlist('tnode01[06-10]')
        self.switches['switch_3'] = hostlist.expand_hostlist('tnode01[11-15]')
        self.switches['switch_4'] = hostlist.expand_hostlist('tnode01[16-20]')


        self.TEMPLATE = jinja2.Template(alltoall_script,
            keep_trailing_newline=True)

        for switch_name in ['switch_1', 'switch_2', 'switch_3', 'switch_4']:
            script_dir = os.path.join(self.switch_test_dir, switch_name)
            os.makedirs(script_dir)

            script_file = os.path.join(script_dir, '{0}.job'.format(switch_name))
            with open(script_file, 'w') as fp:
                fp.write(self.TEMPLATE.render(
                    job_name = 'bench-alltoall-{0}'.format(switch_name),
                    nodes = list(sorted(self.switches[switch_name])),
                    linpack_path = self.alltoall_path,
                    subtest = self.test_name
                ))
            node_list_file = os.path.join(script_dir, 'node_list')
            bench.util.write_node_list(node_list_file, list(sorted(self.switches[switch_name])))


    def tearDown (self):
        shutil.rmtree(self.directory)

    def get_switch_name(self, num):
        return 'switch_' + str(num + 1)


    def test_submit_jobs_1(self, arg1):
        '''Test submit of alltoall-switch jobs with no extra arguments'''
        switch_test = bench.tests.node_test.NodeTest("alltoall-switch")
        switch_test.Submit.execute(self.directory)

        self.assertTrue(bench.slurm.sbatch.called)

        for ii, call in enumerate(arg1.call_args_list):
            switch_name = self.get_switch_name(ii)
            script_dir = os.path.join(self.switch_test_dir, switch_name)
            args, kwargs = call #call object is two things: args=tuple, kwargs=dict
            self.assertEqual(kwargs['chdir'], script_dir)
            self.assertEqual(args[0], script_dir + '/' + switch_name + '.job')
            self.assertFalse('reservation' in kwargs)


    def test_submit_jobs_2(self, arg1):
        '''Test submit of alltoall-switch jobs with an account, qos, and reservation'''
        switch_test = bench.tests.node_test.NodeTest("alltoall-switch")
        switch_test.Submit.execute(self.directory, reservation='fake_res',
                         account='fake_account', qos='fake_qos')

        self.assertTrue(bench.slurm.sbatch.called)

        for ii, call in enumerate(arg1.call_args_list):
            switch_name = self.get_switch_name(ii)
            script_dir = os.path.join(self.switch_test_dir, switch_name)
            args, kwargs = call #call object is two things: args=tuple, kwargs=dict
            self.assertEqual(kwargs['chdir'], script_dir)
            self.assertEqual(args[0], script_dir + '/' + switch_name + '.job')
            self.assertEqual(kwargs['reservation'], 'fake_res')
            self.assertEqual(kwargs['account'], 'fake_account')
            self.assertEqual(kwargs['qos'], 'fake_qos')

    def test_submit_jobs_3(self, arg1):
        '''Test submit of alltoall-switch jobs with nodes in --nodelist
        Only tests will ALL nodes in --nodelist should be submitted'''
        switch_test = bench.tests.node_test.NodeTest("alltoall-switch")
        switch_test.Submit.execute(self.directory, nodelist='tnode01[01-12]')

        self.assertTrue(bench.slurm.sbatch.called)

        for ii, call in enumerate(arg1.call_args_list):
            switch_name = self.get_switch_name(ii)
            script_dir = os.path.join(self.switch_test_dir, switch_name)
            args, kwargs = call #call object is two things: args=tuple, kwargs=dict
            self.assertEqual(kwargs['chdir'], script_dir)
            self.assertEqual(args[0], script_dir + '/' + switch_name + '.job')
            # Check that --nodelist nodes not submitted
            for switch in ['switch_3', 'switch_4']:
                self.assertNotIn(switch, kwargs['chdir'])

















#
