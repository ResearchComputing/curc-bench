import bench.driver
import argparse
import mock
import unittest
from bench.tests.node_test import NodeTest
from bench.framework_add import Add
from bench.framework_submit import Submit

class TestDriver(unittest.TestCase):

    def setUp(self):
        self.parser = bench.driver.parser()

    @mock.patch('bench.log.configure_stderr_logging',
        return_value=None)
    def test_parser_add(self, *arg):
        '''Test that arguments are being parsed as expected'''
        parsed = self.parser.parse_args(['-d', 'fake_dir',
                                '-v', 'add', '--test', 'node'])
        self.assertEqual(parsed.command, 'add')
        self.assertEqual(parsed.test, 'node')
        self.assertEqual(parsed.verbose, True)
        self.assertEqual(parsed.directory, 'fake_dir')


    @mock.patch('bench.driver.get_directory',
        return_value='fake_dir')
    @mock.patch('bench.log.configure_stderr_logging',
        return_value=None)
    @mock.patch('bench.log.configure_file_logging',
        return_value=None)
    @mock.patch('bench.framework_add.Add.execute',
        return_value=None)
    def test_call_bench_add_execute_1(self, *arg):
        '''Test that bench.tests.node_test.NodeTest Add.execute is being called'''
        bench.driver.driver(argv=['bench', 'add', '--test', 'node'])
        assert Add.execute.called
        assert 'fake_dir' in Add.execute.call_args[0]


    @mock.patch('bench.driver.get_directory',
        return_value='fake_dir')
    @mock.patch('bench.log.configure_stderr_logging',
        return_value=None)
    @mock.patch('bench.log.configure_file_logging',
        return_value=None)
    @mock.patch('bench.framework_submit.Submit.execute',
        return_value=None)
    # @mock.patch('bench.tests.node_test.NodeTest',
    #     return_value=None)
    def test_call_bench_submit_execute_1(self, *arg):
        '''Test that bench.tests.node_test.NodeTest Submit.execute is being called correctly with
        a specified reservation'''
        bench.driver.driver(argv=['bench', 'submit', '--test', 'node',
            '--reservation', 'fake_reservation'])
        #print("Submit args", Submit.execute.call_args)
        assert Submit.execute.called
        assert 'fake_dir' in Submit.execute.call_args[0]
        self.assertEqual(Submit.execute.call_args[1]['reservation'],
             'fake_reservation')


    @mock.patch('bench.driver.get_directory',
        return_value='fake_dir')
    @mock.patch('bench.log.configure_stderr_logging',
        return_value=None)
    @mock.patch('bench.log.configure_file_logging',
        return_value=None)
    @mock.patch('bench.framework_submit.Submit.execute',
        return_value=None)
    @mock.patch.dict(bench.configuration.config, {'submit': {'account' : 'default_account',
                                                    'qos' : 'default_qos'}})
    def test_call_bench_submit_execute_2(self, *arg):
        '''Test that bench.tests.node_test.NodeTest Submit.execute correctly uses
        default configuration'''
        bench.driver.driver(argv=['bench', 'submit', '--test', 'node'])
        assert Submit.execute.called
        assert 'fake_dir' in Submit.execute.call_args[0]
        self.assertEqual(Submit.execute.call_args[1]['account'],
             'default_account')
        self.assertEqual(Submit.execute.call_args[1]['qos'],
             'default_qos')
        self.assertEqual(Submit.execute.call_args[1]['reservation'],
             None)

    @mock.patch('bench.driver.get_directory',
        return_value='fake_dir')
    @mock.patch('bench.log.configure_stderr_logging',
        return_value=None)
    @mock.patch('bench.log.configure_file_logging',
        return_value=None)
    @mock.patch('bench.framework_submit.Submit.execute',
        return_value=None)
    @mock.patch.dict(bench.configuration.config, {'submit': {'account' : 'default_account',
                                                    'qos' : 'default_qos'}})
    def test_call_bench_submit_execute_3(self, *arg):
        '''Test that bench.tests.node_test.NodeTest Submit.execute correctly overrides
        default configuration when arguments are added from command line'''
        bench.driver.driver(argv=['bench', 'submit', '--test', 'node',
            '--account', 'fake_account', '--qos', 'fake_qos',
            '--reservation', 'fake_reservation'])
        assert Submit.execute.called
        assert 'fake_dir' in Submit.execute.call_args[0]
        self.assertEqual(Submit.execute.call_args[1]['account'],
             'fake_account')
        self.assertEqual(Submit.execute.call_args[1]['qos'],
             'fake_qos')
        self.assertEqual(Submit.execute.call_args[1]['reservation'],
             'fake_reservation')













#
