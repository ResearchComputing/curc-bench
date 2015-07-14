import bench.tests.alltoall
import os
import pkg_resources
import shutil
import tempfile
import unittest


OSU_ALLTOALL_OUTPUT = pkg_resources.resource_string(__name__, 'osu_alltoall.out')


class TestAllToAllProcess (unittest.TestCase):

    def setUp (self):
        self.prefix = tempfile.mkdtemp()
        self.test_dir = tempfile.mkdtemp(dir=self.prefix)
        self.osu_alltoall = os.path.join(self.test_dir, 'osu_alltoall.out')
        with open(self.osu_alltoall, 'w') as fp:
            pass # just create the file
        assert os.path.exists(self.osu_alltoall)
        self.node_list = os.path.join(self.test_dir, 'node_list')
        with open(self.node_list, 'w') as fp:
            fp.write('tnode1\n')

    def tearDown (self):
        if os.path.exists(self.prefix):
            shutil.rmtree(self.prefix)

    def test_empty (self):
        result = bench.tests.alltoall.process([], self.prefix)
        self.assertEqual(result['pass_nodes'], set())
        self.assertEqual(result['fail_nodes'], set(['tnode1']))
        self.assertEqual(result['error_nodes'], set())

    def test_garbage (self):
        with open(self.osu_alltoall, 'w') as fp:
            fp.write('asfd\nhjkl\n')
        result = bench.tests.alltoall.process([], self.prefix)
        self.assertEqual(result['pass_nodes'], set())
        self.assertEqual(result['fail_nodes'], set(['tnode1']))
        self.assertEqual(result['error_nodes'], set())



class TestAllToAll (unittest.TestCase):

    def test_parse_osu_alltoall (self):
        data = list(bench.tests.alltoall.parse_osu_alltoall(OSU_ALLTOALL_OUTPUT))
        self.assertEqual(len(data), 100)
        for datum in data:
            self.assertEqual(len(datum), 5)
            self.assertEqual(datum[-1], 100)

    def test_evaluate_osu_alltoall (self):
        pass_ = bench.tests.alltoall.evaluate_osu_alltoall(
            bench.tests.alltoall.parse_osu_alltoall(OSU_ALLTOALL_OUTPUT), 2)
