import bench.tests.bandwidth
import os
import shutil
import tempfile
import unittest


class TestBandwidthGenerate (unittest.TestCase):

    def setUp (self):
        self.prefix = tempfile.mkdtemp()

    def test_one (self):
        result = bench.tests.bandwidth.generate(['tnode1'], self.prefix, {'tsw1': set(['tnode1'])})
        self.assertEqual(os.listdir(self.prefix), [])


class TestBandwidthProcess (unittest.TestCase):

    def setUp (self):
        self.prefix = tempfile.mkdtemp()
        self.test_dir = tempfile.mkdtemp(dir=self.prefix)
        self.osu_bw = os.path.join(self.test_dir, 'osu_bw.out')
        with open(self.osu_bw, 'w') as fp:
            pass # just create the file
        assert os.path.exists(self.osu_bw)
        self.node_list = os.path.join(self.test_dir, 'node_list')
        with open(self.node_list, 'w') as fp:
            fp.write('tnode1\n')

    def tearDown (self):
        if os.path.exists(self.prefix):
            shutil.rmtree(self.prefix)

    def test_empty (self):
        result = bench.tests.bandwidth.process([], self.prefix)
        self.assertEqual(result['pass_nodes'], set())
        self.assertEqual(result['fail_nodes'], set(['tnode1']))
        self.assertEqual(result['error_nodes'], set())

    def test_garbage (self):
        with open(self.osu_bw, 'w') as fp:
            fp.write('asfd\nhjkl\n')
        result = bench.tests.bandwidth.process([], self.prefix)
        self.assertEqual(result['pass_nodes'], set())
        self.assertEqual(result['fail_nodes'], set(['tnode1']))
        self.assertEqual(result['error_nodes'], set())
