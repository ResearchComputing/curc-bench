import bench.reserve
import mock
import os
import shutil
import subprocess
import tempfile
import unittest


def fake_Popen():
    popen = mock.Mock()
    popen.communicate = lambda: ('', '')
    popen.returncode = 0
    return popen


class TestReserveExecute (unittest.TestCase):

    def setUp (self):
        self.directory = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.directory, 'node'))
        with open(os.path.join(self.directory, 'node', 'bad_nodes'), 'w') as fp:
            for node in ('tnode0101', 'tnode0102'):
                fp.write('{0}\n'.format(node))
        with open(os.path.join(self.directory, 'node', 'not_tested'), 'w') as fp:
            for node in ('tnode0103', 'tnode0104'):
                fp.write('{0}\n'.format(node))

    def tearDown (self):
        shutil.rmtree(self.directory)


    @mock.patch('bench.reserve.bench.slurm.subprocess.Popen',
                return_value=fake_Popen())
    def test_default (self, popen):
        bench.reserve.execute(self.directory)
        popen.assert_called_once_with(['scontrol', 'create',
                                       'reservation=bench-node',
                                       'accounts=crcbenchmark',
                                       'flags=overlap',
                                       'starttime=now',
                                       'nodes=tnode0101,tnode0102,tnode0103,tnode0104'],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)

    @mock.patch('bench.reserve.bench.slurm.subprocess.Popen',
                return_value=fake_Popen())
    def test_bad_nodes (self, popen):
        bench.reserve.execute(self.directory, bad_nodes=True)
        popen.assert_called_once_with(['scontrol', 'create',
                                       'reservation=bench-node',
                                       'accounts=crcbenchmark',
                                       'flags=overlap',
                                       'starttime=now',
                                       'nodes=tnode0101,tnode0102'],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)

    @mock.patch('bench.reserve.bench.slurm.subprocess.Popen',
                return_value=fake_Popen())
    def test_not_tested (self, popen):
        bench.reserve.execute(self.directory, not_tested=True)
        popen.assert_called_once_with(['scontrol', 'create',
                                       'reservation=bench-node',
                                       'accounts=crcbenchmark',
                                       'flags=overlap',
                                       'starttime=now',
                                       'nodes=tnode0103,tnode0104'],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)


    @mock.patch('bench.reserve.bench.slurm.subprocess.Popen',
                return_value=fake_Popen())
    def test_bad_nodes_and_not_tested (self, popen):
        bench.reserve.execute(self.directory, bad_nodes=True, not_tested=True)
        popen.assert_called_once_with(['scontrol', 'create',
                                       'reservation=bench-node',
                                       'accounts=crcbenchmark',
                                       'flags=overlap',
                                       'starttime=now',
                                       'nodes=tnode0101,tnode0102,tnode0103,tnode0104'],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
