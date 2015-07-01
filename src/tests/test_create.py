import bench.create
import datetime
import mock
import os
import shutil
import tempfile
import unittest


def fake_node (node_dict):
    node = mock.Mock()
    for node_name, node_ in node_dict.iteritems():
        if 'name' not in node_:
            node_['name'] = node_name
        if 'node_state' not in node_:
            node_['node_state'] = 'IDLE'
    node.get = mock.Mock(return_value=node_dict)
    return node


def fake_reservation (reservation_dict):
    reservation = mock.Mock()
    reservation.get = mock.Mock(return_value=reservation_dict)
    return reservation


class TestCreateExecute (unittest.TestCase):

    def setUp (self):
        self.directory = tempfile.mkdtemp()

    def tearDown (self):
        shutil.rmtree(self.directory)

    @mock.patch('bench.create.bench.util.pyslurm.node',
                return_value=fake_node({'tnode0101': {}, 'tnode0102': {}}))
    def test_execute (self, _):
        bench.create.execute(self.directory)
        node_list = os.path.join(self.directory, 'node_list')
        self.assertTrue(os.path.exists(node_list), node_list)
        self.assertEqual(open(node_list).read(), 'tnode0101\ntnode0102\n')

    @mock.patch('bench.create.bench.util.pyslurm.node',
                return_value=fake_node({'tnode0101': {}, 'tnode0102': {}}))
    def test_include_nodes (self, _):
        bench.create.execute(self.directory, include_nodes=['tnode0101'])
        node_list = os.path.join(self.directory, 'node_list')
        self.assertTrue(os.path.exists(node_list), node_list)
        self.assertEqual(open(node_list).read(), 'tnode0101\n')

    @mock.patch('bench.create.bench.util.pyslurm.node',
                return_value=fake_node({'tnode0101': {}, 'tnode0102': {}, 'tnode0103': {}}))
    def test_include_nodes_pattern (self, _):
        bench.create.execute(self.directory, include_nodes=['tnode01[02-03]'])
        node_list = os.path.join(self.directory, 'node_list')
        self.assertTrue(os.path.exists(node_list), node_list)
        self.assertEqual(open(node_list).read(), 'tnode0102\ntnode0103\n')

    @mock.patch('bench.create.bench.util.pyslurm.node',
                return_value=fake_node({'tnode0101': {}, 'tnode0102': {}}))
    def test_exclude_nodes (self, _):
        bench.create.execute(self.directory, exclude_nodes=['tnode0101'])
        node_list = os.path.join(self.directory, 'node_list')
        self.assertTrue(os.path.exists(node_list), node_list)
        self.assertEqual(open(node_list).read(), 'tnode0102\n')

    @mock.patch('bench.create.bench.util.pyslurm.node',
                return_value=fake_node({'tnode0101': {}, 'tnode0102': {}, 'tnode0103': {}}))
    def test_exclude_nodes_pattern (self, _):
        bench.create.execute(self.directory, exclude_nodes=['tnode01[01-02]'])
        node_list = os.path.join(self.directory, 'node_list')
        self.assertTrue(os.path.exists(node_list), node_list)
        self.assertEqual(open(node_list).read(), 'tnode0103\n')

    @mock.patch('bench.create.bench.util.pyslurm.node',
                return_value=fake_node({'tnode0101': {}, 'tnode0102': {}, 'tnode0103': {}}))
    def test_include_exclude_nodes (self, _):
        bench.create.execute(self.directory,
                             include_nodes=['tnode01[01-02]'],
                             exclude_nodes=['tnode0101'])
        node_list = os.path.join(self.directory, 'node_list')
        self.assertTrue(os.path.exists(node_list), node_list)
        self.assertEqual(open(node_list).read(), 'tnode0102\n')

    @mock.patch('bench.create.bench.util.pyslurm.node',
                return_value=fake_node({'tnode0101': {}, 'tnode0102': {}, 'tnode0103': {}}))
    @mock.patch('bench.create.bench.util.pyslurm.reservation',
                return_value=fake_reservation({'res1': {'node_list': 'tnode0101,tnode0103'}}))
    def test_include_reservation (self, _n, _r):
        bench.create.execute(self.directory,
                             include_reservations=['res1'])
        node_list = os.path.join(self.directory, 'node_list')
        self.assertTrue(os.path.exists(node_list), node_list)
        self.assertEqual(open(node_list).read(), 'tnode0101\ntnode0103\n')

    @mock.patch('bench.create.bench.util.pyslurm.node',
                return_value=fake_node({'tnode0101': {}, 'tnode0102': {}, 'tnode0103': {}}))
    @mock.patch('bench.create.bench.util.pyslurm.reservation',
                return_value=fake_reservation({'res1': {'node_list': 'tnode0101,tnode0103'}}))
    def test_include_reservation_include_nodes (self, _n, _r):
        bench.create.execute(self.directory,
                             include_reservations=['res1'],
                             include_nodes=['tnode0102'])
        node_list = os.path.join(self.directory, 'node_list')
        self.assertTrue(os.path.exists(node_list), node_list)
        self.assertEqual(open(node_list).read(), 'tnode0101\ntnode0102\ntnode0103\n')

    @mock.patch('bench.create.bench.util.pyslurm.node',
                return_value=fake_node({'tnode0101': {}, 'tnode0102': {}, 'tnode0103': {}}))
    @mock.patch('bench.create.bench.util.pyslurm.reservation',
                return_value=fake_reservation({'res1': {'node_list': 'tnode0101,tnode0103'}}))
    def test_include_reservation_exclude_nodes (self, _n, _r):
        bench.create.execute(self.directory,
                             include_reservations=['res1'],
                             exclude_nodes=['tnode0101'])
        node_list = os.path.join(self.directory, 'node_list')
        self.assertTrue(os.path.exists(node_list), node_list)
        self.assertEqual(open(node_list).read(), 'tnode0103\n')

    @mock.patch('bench.create.bench.util.pyslurm.node',
                return_value=fake_node({'tnode0101': {}, 'tnode0102': {}, 'tnode0103': {}}))
    @mock.patch('bench.create.bench.util.pyslurm.reservation',
                return_value=fake_reservation({'res1': {'node_list': 'tnode0101,tnode0103'}}))
    def test_exclude_reservation (self, _n, _r):
        bench.create.execute(self.directory,
                             exclude_reservations=['res1'])
        node_list = os.path.join(self.directory, 'node_list')
        self.assertTrue(os.path.exists(node_list), node_list)
        self.assertEqual(open(node_list).read(), 'tnode0102\n')

    @mock.patch('bench.create.bench.util.pyslurm.node',
                return_value=fake_node({'tnode0101': {}, 'tnode0102': {}, 'tnode0103': {}}))
    @mock.patch('bench.create.bench.util.pyslurm.reservation',
                return_value=fake_reservation({'res1': {'node_list': 'tnode0101,tnode0103'}}))
    def test_exclude_reservation_include_nodes (self, _n, _r):
        bench.create.execute(self.directory,
                             exclude_reservations=['res1'],
                             include_nodes=['tnode0101'])
        node_list = os.path.join(self.directory, 'node_list')
        self.assertTrue(os.path.exists(node_list), node_list)
        self.assertEqual(open(node_list).read(), '')

    @mock.patch('bench.create.bench.util.pyslurm.node',
                return_value=fake_node({'tnode0101': {}, 'tnode0102': {}, 'tnode0103': {}}))
    @mock.patch('bench.create.bench.util.pyslurm.reservation',
                return_value=fake_reservation({'res1': {'node_list': 'tnode0101,tnode0103'}}))
    def test_exclude_reservation_exclude_nodes (self, _n, _r):
        bench.create.execute(self.directory,
                             exclude_reservations=['res1'],
                             exclude_nodes=['tnode0102'])
        node_list = os.path.join(self.directory, 'node_list')
        self.assertTrue(os.path.exists(node_list), node_list)
        self.assertEqual(open(node_list).read(), '')
