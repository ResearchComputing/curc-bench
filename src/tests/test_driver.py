import bench.driver
import argparse
import mock
import unittest

class TestDriver(unittest.TestCase):

    def setUp(self):
        self.parser = bench.driver.parser()

    @mock.patch('bench.log.configure_stderr_logging',
        return_value=None)
    def test_parser_add(self, *arg):
        '''Test that arguments are being parsed as expected'''
        parsed = self.parser.parse_args(['-d', 'fake_dir',
                                '-v', 'add', '--node-tests'])
        self.assertEqual(parsed.command, 'add')
        self.assertEqual(parsed.node_tests, True)
        self.assertEqual(parsed.verbose, True)
        self.assertEqual(parsed.directory, 'fake_dir')

    @mock.patch('bench.driver.get_directory',
        return_value='fake_dir')
    @mock.patch('bench.log.configure_stderr_logging',
        return_value=None)
    @mock.patch('bench.log.configure_file_logging',
        return_value=None)
    @mock.patch('bench.add.execute',
        return_value=None)
    def test_call_bench_add_execute_1(self, *arg):
        '''Test that bench.add.execute is being called correctly WITH
        a specified topology file'''
        bench.driver.driver(argv=['bench', 'add', '--bandwidth-tests', 
            '-t', 'fake_topology_file'])
        assert bench.add.execute.called
        assert 'fake_dir' in bench.add.execute.call_args[0]
        assert 'fake_topology_file' in bench.add.execute.call_args[0]
        assert bench.add.execute.call_args[1]['bandwidth_tests']

    @mock.patch('bench.driver.get_directory',
        return_value='fake_dir')
    @mock.patch('bench.log.configure_stderr_logging',
        return_value=None)
    @mock.patch('bench.log.configure_file_logging',
        return_value=None)
    @mock.patch('bench.add.execute',
        return_value=None)
    @mock.patch('os.environ.get',
        return_value='fake_topology_file')
    def test_call_bench_add_execute_2(self, *arg):
        '''Test that bench.add.execute is being called correctly WITHOUT
        a specified topology file'''
        bench.driver.driver(argv=['bench', 'add', '--bandwidth-tests'])
        assert bench.add.execute.called
        assert 'fake_dir' in bench.add.execute.call_args[0]
        assert 'fake_topology_file' in bench.add.execute.call_args[0]
        assert bench.add.execute.call_args[1]['bandwidth_tests']


    @mock.patch('bench.driver.get_directory',
        return_value='fake_dir')
    @mock.patch('bench.log.configure_stderr_logging',
        return_value=None)
    @mock.patch('bench.log.configure_file_logging',
        return_value=None)
    @mock.patch('bench.submit.execute',
        return_value=None)
    def test_call_bench_submit_execute_1(self, *arg):
        '''Test that bench.submit.execute is being called correctly WITH
        a specified reservation'''
        bench.driver.driver(argv=['bench', 'submit', '--node-tests', 
            '--reservation', 'fake_reservation'])
        assert bench.submit.execute.called
        assert 'fake_dir' in bench.submit.execute.call_args[0]
        assert bench.submit.execute.call_args[1]['node_tests']
        self.assertEqual(bench.submit.execute.call_args[1]['reservation'], 
            'fake_reservation')

    @mock.patch('bench.driver.get_directory',
        return_value='fake_dir')
    @mock.patch('bench.log.configure_stderr_logging',
        return_value=None)
    @mock.patch('bench.log.configure_file_logging',
        return_value=None)
    @mock.patch('bench.submit.execute',
        return_value=None)
    @mock.patch('os.environ.get',
        return_value='fake_reservation')
    def test_call_bench_submit_execute_2(self, *arg):
        '''Test that bench.submit.execute is being called correctly WITHOUT
        a specified reservation'''
        bench.driver.driver(argv=['bench', 'submit', '--node-tests'])
        assert bench.submit.execute.called
        assert 'fake_dir' in bench.submit.execute.call_args[0]
        assert bench.submit.execute.call_args[1]['node_tests']
        self.assertEqual(bench.submit.execute.call_args[1]['reservation'], 
            'fake_reservation')
