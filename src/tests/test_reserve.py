import bench.reserve
import mock
import os
import shutil
import tempfile
import unittest


class TestReserveExecute (unittest.TestCase):

    def setUp (self):
        self.directory = tempfile.mkdtemp()

    def tearDown (self):
        shutil.rmtree(self.directory)

    @mock.patch('bench.reserve.pyslurm.slurm_create_reservation')
    def test_node (self, create_reservation):
        os.mkdir(os.path.join(self.directory, 'node'))
        with open(os.path.join(self.directory, 'node', 'bad_nodes'), 'w') as fp:
            for node in ('node0101', 'node0102'):
                fp.write('{0}\n'.format(node))
        
        bench.reserve.execute(self.directory, node_tests=True)
        self.assertEqual(create_reservation.call_args[0][0]['node_list'], 'node0101,node0102')
        self.assertEqual(create_reservation.call_args[0][0]['node_cnt'], 2)
