import bench.tests.alltoall
import pkg_resources
import unittest


OSU_ALLTOALL_OUTPUT = pkg_resources.resource_string(__name__, 'osu_alltoall.out')


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
