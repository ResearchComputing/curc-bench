import bench.infiniband
import unittest


class TestGetNodePairs (unittest.TestCase):

    def assertIn (self, item, collection):
        assert item in collection, '{0} not in {1}'.format(item, collection)

    def test_empty (self):
        pairs = list(bench.infiniband.get_node_pairs([]))
        self.assertEqual(pairs, [])

    def test_even (self):
        pairs = list(bench.infiniband.get_node_pairs(['tnode1', 'tnode2', 'tnode3', 'tnode4']))
        self.assertEqual(pairs, [
            set(['tnode1', 'tnode2']),
            set(['tnode3', 'tnode4']),
        ])

    def test_odd (self):
        pairs = list(bench.infiniband.get_node_pairs(['tnode1', 'tnode2', 'tnode3']))
        self.assertEqual(pairs[0], set(['tnode1', 'tnode2']))
        self.assertIn('tnode3', pairs[1])
        self.assertNotEqual(pairs[1] & set(['tnode1', 'tnode2']), set())
