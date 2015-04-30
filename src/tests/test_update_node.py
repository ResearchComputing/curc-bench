import bench.update_nodes
import mock
import os
import pyslurm
import shutil
import subprocess
import tempfile
import unittest


def fake_pyslurm_node():
    node = mock.Mock()
    node.find_id = mock.Mock(return_value={'node_state':'IDLE'})
    node.update = mock.Mock()
    return node


class TestUpdateNodeUpdate (unittest.TestCase):

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


    @mock.patch('bench.update_nodes.pyslurm.node',
                return_value=fake_pyslurm_node())
    def test_default (self, pyslurm_node):
        bench.update_nodes.update_nodes(self.directory)
        self.assertEqual(
            pyslurm_node.return_value.update.call_args_list,
            [
                mock.call({'reason': 'bench:node', 'node_names': 'tnode0101', 'node_state': pyslurm.NODE_STATE_DRAIN}),
                mock.call({'reason': 'bench:node', 'node_names': 'tnode0102', 'node_state': pyslurm.NODE_STATE_DRAIN}),
                mock.call({'reason': 'bench:node', 'node_names': 'tnode0103', 'node_state': pyslurm.NODE_STATE_DRAIN}),
                mock.call({'reason': 'bench:node', 'node_names': 'tnode0104', 'node_state': pyslurm.NODE_STATE_DRAIN}),
            ])

    @mock.patch('bench.update_nodes.pyslurm.node',
                return_value=fake_pyslurm_node())
    def test_bad_nodes (self, pyslurm_node):
        bench.update_nodes.update_nodes(self.directory, bad_nodes=True)
        self.assertEqual(
            pyslurm_node.return_value.update.call_args_list,
            [
                mock.call({'reason': 'bench:node', 'node_names': 'tnode0101', 'node_state': pyslurm.NODE_STATE_DRAIN}),
                mock.call({'reason': 'bench:node', 'node_names': 'tnode0102', 'node_state': pyslurm.NODE_STATE_DRAIN}),
            ])

    @mock.patch('bench.update_nodes.pyslurm.node',
                return_value=fake_pyslurm_node())
    def test_not_tested (self, pyslurm_node):
        bench.update_nodes.update_nodes(self.directory, not_tested=True)
        self.assertEqual(
            pyslurm_node.return_value.update.call_args_list,
            [
                mock.call({'reason': 'bench:node', 'node_names': 'tnode0103', 'node_state': pyslurm.NODE_STATE_DRAIN}),
                mock.call({'reason': 'bench:node', 'node_names': 'tnode0104', 'node_state': pyslurm.NODE_STATE_DRAIN}),
            ])


    @mock.patch('bench.update_nodes.pyslurm.node',
                return_value=fake_pyslurm_node())
    def test_bad_nodes_and_not_tested (self, pyslurm_node):
        bench.update_nodes.update_nodes(self.directory, bad_nodes=True, not_tested=True)
        self.assertEqual(
            pyslurm_node.return_value.update.call_args_list,
            [
                mock.call({'reason': 'bench:node', 'node_names': 'tnode0101', 'node_state': pyslurm.NODE_STATE_DRAIN}),
                mock.call({'reason': 'bench:node', 'node_names': 'tnode0102', 'node_state': pyslurm.NODE_STATE_DRAIN}),
                mock.call({'reason': 'bench:node', 'node_names': 'tnode0103', 'node_state': pyslurm.NODE_STATE_DRAIN}),
                mock.call({'reason': 'bench:node', 'node_names': 'tnode0104', 'node_state': pyslurm.NODE_STATE_DRAIN}),
            ])
