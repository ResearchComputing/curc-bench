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

job_script = '''#!/bin/bash
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

@mock.patch('bench.slurm.sbatch', return_value="Submitted batch job")
class TestSubmit(unittest.TestCase):

    def assertIsFile (self, path):
        assert os.path.isfile(path), '{0} does not exist'.format(path)

    def setUp (self):
        self.directory = tempfile.mkdtemp()
        self.node_dir = os.path.join(self.directory, 'node')
        self.node_test_dir = os.path.join(self.node_dir, 'tests')

        os.mkdir(self.node_dir)
        os.mkdir(self.node_test_dir)

        self.nodes = ['tnode01{0:02}'.format(i) for i in range(1, num_nodes)]
        self.bench_node_list = os.path.join(self.directory, 'node_list')
        bench.util.write_node_list(os.path.join(self.directory, 'node_list'),
                                   self.nodes)
        bench.util.write_node_list(os.path.join(self.node_dir, 'node_list'),
                                   self.nodes)

        self.linpack_path = '/fake/linpack.so'
        self.stream_path = '/fake/stream.so'

        self.TEMPLATE = jinja2.Template(job_script,
            keep_trailing_newline=True)

        for ii in range(0, num_nodes - 1):
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

    def tearDown (self):
        shutil.rmtree(self.directory)


    def test_submit_jobs(self, arg1):
        node_test = bench.tests.node_test.NodeTest("node")
        node_test.Submit.execute(self.directory)#, reservation="fake_res")

        self.assertTrue(bench.slurm.sbatch.called)

        for ii, call in enumerate(arg1.call_args_list):
            script_dir = os.path.join(self.node_test_dir, self.nodes[ii])
            args, kwargs = call #call object is two things: args=tuple, kwargs=dict
            self.assertEqual(kwargs['workdir'], script_dir)
            self.assertEqual(args[0], script_dir + '/' + self.nodes[ii] + '.job')
            self.assertFalse('reservation' in kwargs)





























#
