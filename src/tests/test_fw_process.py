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

from random import uniform

linpack_output = '''Intel(R) Optimized LINPACK Benchmark data

Current date/time: Wed Apr  4 17:47:58 2018

CPU frequency:    1.189 GHz
Number of CPUs: 2
Number of cores: 24
Number of threads: 24

Parameters are set to:

Number of tests: 6
Number of equations to solve (problem size) : 1000  5000  10000 20000 25000 150000
Leading dimension of array                  : 1000  5000  10000 20000 25000 150000
Number of trials to run                     : 2     2     2     1     1     1
Data alignment value (in Kbytes)            : 4     4     4     4     4     4

Maximum memory requested that can be used=5000504096, at the size=25000

=================== Timing linear equation system solver ===================

Size   LDA    Align. Time(s)    GFlops   Residual     Residual(norm) Check
1000   1000   4      0.040      16.7099  9.298812e-13 3.171134e-02   pass
1000   1000   4      0.022      29.9527  9.298812e-13 3.171134e-02   pass
5000   5000   4      0.451      185.0853 2.334886e-11 3.255810e-02   pass
5000   5000   4      0.307      271.2428 2.334886e-11 3.255810e-02   pass
10000  10000  4      1.975      337.7092 1.070743e-10 3.775550e-02   pass
10000  10000  4      1.968      338.8993 1.070743e-10 3.775550e-02   pass
20000  20000  4      14.149     376.9962 4.102256e-10 3.631395e-02   pass
25000  25000  4      27.327     381.2373 5.691514e-10 3.236560e-02   pass

Performance Summary (GFlops)

Size   LDA    Align.  Average  Maximal
1000   1000   4       5  29.9527
5000   5000   4       {avg_5k} 271.2428
10000  10000  4       {avg_10k} 338.8993
20000  20000  4       {avg_20k} 376.9962
25000  25000  4       {avg_25k} 381.2373

Residual checks PASSED

End of tests
'''

stream_output = '''
-------------------------------------------------------------
STREAM version $Revision: 5.9 $
-------------------------------------------------------------
This system uses 8 bytes per DOUBLE PRECISION word.
-------------------------------------------------------------
Array size = 512000000, Offset = 0
Total memory required = 11718.8 MB.
Each test is run 10 times, but only
the *best* time for each is used.
-------------------------------------------------------------
Number of Threads requested = 24
-------------------------------------------------------------
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
Printing one line per active thread....
-------------------------------------------------------------
Your clock granularity/precision appears to be 1 microseconds.
Each test below will take on the order of 115574 microseconds.
   (= 115574 clock ticks)
Increase the size of the arrays if this shows that
you are not getting at least 20 clock ticks per test.
-------------------------------------------------------------
WARNING -- The above is only a rough guideline.
For best results, please be sure you know the
precision of your system timer.
-------------------------------------------------------------
Function      Rate (MB/s)   Avg time     Min time     Max time
Copy:        {copy_avg}       0.1         0.1393       0.1405
Scale:       {scale_avg}      0.1         0.1354       0.1360
Add:         {add_avg}        0.1         0.1981       0.1996
Triad:       {triad_avg}      0.1         0.1980       0.1991
-------------------------------------------------------------
Solution Validates
-------------------------------------------------------------
'''

class TestProcess(unittest.TestCase):

    def assertIsFile (self, path):
        assert os.path.isfile(path), '{0} does not exist'.format(path)

    def setUp (self):
        self.directory = tempfile.mkdtemp()
        self.node_dir = os.path.join(self.directory, 'node')
        self.node_test_dir = os.path.join(self.node_dir, 'tests')

        os.mkdir(self.node_dir)
        os.mkdir(self.node_test_dir)

        self.num_nodes = 11

        self.nodes = ['tnode01{0:02}'.format(i) for i in range(1, self.num_nodes)]
        self.pass_node_range = [1, 5]
        self.fail_node_range = [self.pass_node_range[1], 9]
        self.error_node_range = [self.fail_node_range[1], self.num_nodes]
        self.pass_nodes = ['tnode01{0:02}'.format(i) for i in range(self.pass_node_range[0], self.pass_node_range[1])]
        self.fail_nodes = ['tnode01{0:02}'.format(i) for i in range(self.fail_node_range[0], self.fail_node_range[1])]
        self.error_nodes = ['tnode01{0:02}'.format(i) for i in range(self.error_node_range[0], self.error_node_range[1])]

        # stream targets
        self.expected_copy = 88000.0
        self.expected_scale = 89000.0
        self.expected_add = 91000.0
        self.expected_triad = 92000.0
        #linpack targets
        self.expected_5k = 380.0
        self.expected_10k = 580.0
        self.expected_20k = 670.0
        self.expected_25k = 640.0


        # Write out fake test data
        for node in self.nodes:
            os.mkdir(os.path.join(self.node_test_dir, node))

            #Passing values
            copy_avg = uniform(self.expected_copy, self.expected_copy*1.3)
            scale_avg = uniform(self.expected_scale, self.expected_scale*1.3)
            add_avg = uniform(self.expected_add, self.expected_add*1.3)
            triad_avg = uniform(self.expected_triad, self.expected_triad*1.3)
            avg_5k = uniform(self.expected_5k, self.expected_5k*1.3)
            avg_10k = uniform(self.expected_10k, self.expected_10k*1.3)
            avg_20k = uniform(self.expected_20k, self.expected_20k*1.3)
            avg_25k = uniform(self.expected_25k, self.expected_25k*1.3)

            #Fail stream
            if node in self.fail_nodes[:len(self.fail_nodes)/2]:
                copy_avg = uniform(0, self.expected_copy - 1)
                scale_avg = uniform(0, self.expected_scale - 1)
                add_avg = uniform(0, self.expected_add - 1)
                triad_avg = uniform(0, self.expected_triad - 1)
            #Fail linpack
            elif node in self.fail_nodes[len(self.fail_nodes)/2:]:
                avg_5k = uniform(0, self.expected_5k - 1)
                avg_10k = uniform(0, self.expected_10k - 1)
                avg_20k = uniform(0, self.expected_20k - 1)
                avg_25k = uniform(0, self.expected_25k - 1)

            if not node in self.error_nodes:
                with open(os.path.join(self.node_test_dir, node, 'stream.out'), 'w') as f:
                    f.write(stream_output.format(copy_avg=copy_avg, scale_avg=scale_avg,
                                add_avg=add_avg, triad_avg=triad_avg))
                    f.close()
                with open(os.path.join(self.node_test_dir, node, 'linpack.out'), 'w') as f:
                    f.write(linpack_output.format(avg_5k=avg_5k, avg_10k=avg_10k,
                                avg_20k=avg_20k, avg_25k=avg_25k))
                    f.close()
            with open(os.path.join(self.node_test_dir, node, 'node_list'), 'w') as f:
                f.write(node)
                f.close()



        self.bench_node_list = os.path.join(self.directory, 'node_list')
        bench.util.write_node_list(os.path.join(self.directory, 'node_list'),
                                   self.nodes)
        bench.util.write_node_list(os.path.join(self.node_dir, 'node_list'),
                                   self.nodes)




    def tearDown (self):
        shutil.rmtree(self.directory)

    def test_write_result_files(self):
        '''Test that pass, fail, and error nodes are written to files'''

        node_test = bench.tests.node_test.NodeTest("node")
        node_test.Process.results_logger = bench.log.setup_logger('results_logger', self.directory, 'results.log')
        node_test.Process.write_result_files(self.node_dir, self.pass_nodes,
                            self.fail_nodes, self.error_nodes)

        pass_node_string = '\n'.join(self.pass_nodes)
        pass_file = open(os.path.join(self.node_dir, 'pass_nodes')).read()
        self.assertIn(pass_node_string, pass_file)

        fail_node_string = '\n'.join(self.fail_nodes)
        fail_file = open(os.path.join(self.node_dir, 'fail_nodes')).read()
        self.assertIn(fail_node_string, fail_file)

        error_node_string = '\n'.join(self.error_nodes)
        error_file = open(os.path.join(self.node_dir, 'error_nodes')).read()
        self.assertIn(error_node_string, error_file)



    def test_process(self):
        '''Test that linpack and stream node tests are parsed and processed
        correctly.'''

        node_test = bench.tests.node_test.NodeTest("node")
        node_test.Process.results_logger = bench.log.setup_logger('results_logger', self.directory, 'results.log')
        node_test.Process.process_tests(self.node_dir)

        for node in self.pass_nodes:
            self.assertIn(node, open(os.path.join(self.node_dir, 'pass_nodes')).read())
        for node in self.fail_nodes:
            self.assertIn(node, open(os.path.join(self.node_dir, 'fail_nodes')).read())
        for node in self.error_nodes:
            self.assertIn(node, open(os.path.join(self.node_dir, 'error_nodes')).read())



















#
