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

    def tearDown (self):
        shutil.rmtree(self.directory)

    @mock.patch('bench.reserve.bench.slurm.subprocess.Popen',
                return_value=fake_Popen())
    def test_node (self, popen):
        os.mkdir(os.path.join(self.directory, 'node'))
        with open(os.path.join(self.directory, 'node', 'bad_nodes'), 'w') as fp:
            for node in ('node0101', 'node0102'):
                fp.write('{0}\n'.format(node))
        
        bench.reserve.execute(self.directory, node_tests=True)
        print repr(popen), dir(popen)
        popen.assert_called_once_with(['scontrol', 'create',
                                       'reservation=bench-node',
                                       'accounts=crcbenchmark',
                                       'flags=overlap',
                                       'starttime=now',
                                       'nodes=node0101,node0102'],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
