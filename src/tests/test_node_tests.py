import bench.exc
import bench.tests.node
import bench.util
import os
import pkg_resources
import shutil
import tempfile
import unittest


STREAM_FAIL = pkg_resources.resource_string(__name__, 'stream.out-fail')
LINPACK_FAIL = pkg_resources.resource_string(__name__, 'linpack.out-fail')
STREAM_PASS = pkg_resources.resource_string(__name__, 'stream.out-pass')
LINPACK_PASS = pkg_resources.resource_string(__name__, 'linpack.out-pass')


class TestParseStream (unittest.TestCase):

    def test_parse_stream (self):
        stream_data = bench.tests.node.parse_stream(STREAM_FAIL)
        copy, scale, add, triad = stream_data
        self.assertAlmostEqual(copy, 21929.6)
        self.assertAlmostEqual(scale, 27922.5)
        self.assertAlmostEqual(add, 31847.4)
        self.assertAlmostEqual(triad, 32180.3)

    def test_parse_invalid_stream (self):
        self.assertRaises(bench.exc.ParseError, bench.tests.node.parse_stream, '')


class TestParseLinpack (unittest.TestCase):

    def test_parse_linpack (self):
        linpack_data = bench.tests.node.parse_linpack(LINPACK_FAIL)
        self.assertEqual(
            set(linpack_data.keys()),
            set([
                (1000, 1000, 4),
                (2000, 2000, 4),
                (5000, 5000, 4),
                (10000, 10000, 4),
                (20000, 20000, 4),
                (25000, 25000, 4),
            ]),
        )
        self.assertAlmostEqual(linpack_data[(1000, 1000, 4)], 11.7745)
        self.assertAlmostEqual(linpack_data[(2000, 2000, 4)], 37.5080)
        self.assertAlmostEqual(linpack_data[(5000, 5000, 4)], 76.4705)
        self.assertAlmostEqual(linpack_data[(10000, 10000, 4)], 85.9916)
        self.assertAlmostEqual(linpack_data[(20000, 20000, 4)], 117.1054)
        self.assertAlmostEqual(linpack_data[(25000, 25000, 4)], 118.4674)

    def test_invalid_linpack (self):
        self.assertRaises(bench.exc.ParseError, bench.tests.node.parse_linpack, '')


class TestEvaluateStream (unittest.TestCase):

    def test_pass_stream (self):
        stream_data = bench.tests.node.parse_stream(STREAM_PASS)
        self.assertTrue(bench.tests.node.evaluate_stream(stream_data))

    def test_fail_stream (self):
        stream_data = bench.tests.node.parse_stream(STREAM_FAIL)
        self.assertFalse(bench.tests.node.evaluate_stream(stream_data))


class TestEvaluateLinpack (unittest.TestCase):

    def test_pass_linpack (self):
        linpack_data = bench.tests.node.parse_linpack(LINPACK_PASS)
        self.assertTrue(bench.tests.node.evaluate_linpack(linpack_data))

    def test_fail_linpack (self):
        linpack_data = bench.tests.node.parse_linpack(LINPACK_FAIL)
        self.assertFalse(bench.tests.node.evaluate_linpack(linpack_data))


class TestNodeProcess (unittest.TestCase):

    def setUp (self):
        self.directory = tempfile.mkdtemp()
        self.prefix = os.path.join(self.directory, 'node')
        self.tests_dir = os.path.join(self.prefix, 'tests')
        bench.util.mkdir_p(self.tests_dir)
        self.nodes = set('node01{0:02}'.format(i) for i in xrange(1, 81))
        self.pass_nodes = set(sorted(self.nodes)[:10])
        self.fail_nodes = set(sorted(self.nodes)[-10:])
        self.assertEqual(len(self.pass_nodes & self.fail_nodes), 0)
        self.error_nodes = self.nodes - (self.pass_nodes | self.fail_nodes)
        with open(os.path.join(self.directory, 'node_list'), 'w') as fp:
            for node in self.nodes:
                fp.write('{0}\n'.format(node))
        for node in self.pass_nodes:
            self._populate_node_list(node)
            self._populate_stream_pass(node)
            self._populate_linpack_pass(node)
        for node in self.fail_nodes:
            self._populate_node_list(node)
            self._populate_stream_fail(node)
            self._populate_linpack_fail(node)

    def tearDown (self):
        shutil.rmtree(self.directory)

    def test_process (self):
        result = bench.tests.node.process(self.nodes, self.tests_dir)
        self.assertEqual(result['fail_nodes'], self.fail_nodes)
        self.assertEqual(result['pass_nodes'], self.pass_nodes)
        self.assertEqual(result['error_nodes'], self.error_nodes)

    def test_missing_stream (self):
        missing_stream_nodes = set(sorted(self.pass_nodes)[:5])
        for node in missing_stream_nodes:
            self._remove_stream(node)
        result = bench.tests.node.process(self.nodes, self.tests_dir)
        self.assertEqual(result['fail_nodes'], self.fail_nodes)
        self.assertEqual(result['pass_nodes'], self.pass_nodes - missing_stream_nodes)
        self.assertEqual(result['error_nodes'], self.error_nodes | missing_stream_nodes)

    def test_missing_linpack (self):
        missing_linpack_nodes = set(sorted(self.pass_nodes)[-5:])
        for node in missing_linpack_nodes:
            self._remove_linpack(node)
        result = bench.tests.node.process(self.nodes, self.tests_dir)
        self.assertEqual(result['fail_nodes'], self.fail_nodes)
        self.assertEqual(result['pass_nodes'], self.pass_nodes - missing_linpack_nodes)
        self.assertEqual(result['error_nodes'], self.error_nodes | missing_linpack_nodes)

    def test_corrupt_stream (self):
        corrupt_stream_nodes = set(sorted(self.pass_nodes)[:5])
        for node in corrupt_stream_nodes:
            self._corrupt_stream(node)
        result = bench.tests.node.process(self.nodes, self.tests_dir)
        self.assertEqual(result['fail_nodes'], self.fail_nodes)
        self.assertEqual(result['pass_nodes'], self.pass_nodes - corrupt_stream_nodes)
        self.assertEqual(result['error_nodes'], self.error_nodes | corrupt_stream_nodes)

    def test_corrupt_linpack (self):
        corrupt_linpack_nodes = set(sorted(self.pass_nodes)[-5:])
        for node in corrupt_linpack_nodes:
            self._corrupt_linpack(node)
        result = bench.tests.node.process(self.nodes, self.tests_dir)
        self.assertEqual(result['fail_nodes'], self.fail_nodes)
        self.assertEqual(result['pass_nodes'], self.pass_nodes - corrupt_linpack_nodes)
        self.assertEqual(result['error_nodes'], self.error_nodes | corrupt_linpack_nodes)

    def _populate_node_list (self, node):
        bench.util.mkdir_p(os.path.join(self.tests_dir, node))
        with open(os.path.join(self.tests_dir, node, 'node_list'), 'w') as fp:
            fp.write('{0}\n'.format(node))

    def _remove_stream (self, node):
        os.remove(os.path.join(self.tests_dir, node, 'stream.out'))

    def _remove_linpack (self, node):
        os.remove(os.path.join(self.tests_dir, node, 'linpack.out'))

    def _corrupt_stream (self, node):
        with open(os.path.join(self.tests_dir, node, 'stream.out'), 'w') as fp:
            fp.write('')

    def _corrupt_linpack (self, node):
        with open(os.path.join(self.tests_dir, node, 'linpack.out'), 'w') as fp:
            fp.write('')

    def _populate_stream_pass (self, node):
        bench.util.mkdir_p(os.path.join(self.tests_dir, node))
        with open(os.path.join(self.tests_dir, node, 'stream.out'), 'w') as fp:
            fp.write(STREAM_PASS)

    def _populate_linpack_pass (self, node):
        bench.util.mkdir_p(os.path.join(self.tests_dir, node))
        with open(os.path.join(self.tests_dir, node, 'linpack.out'), 'w') as fp:
            fp.write(LINPACK_PASS)

    def _populate_stream_fail (self, node):
        bench.util.mkdir_p(os.path.join(self.tests_dir, node))
        with open(os.path.join(self.tests_dir, node, 'stream.out'), 'w') as fp:
            fp.write(STREAM_FAIL)

    def _populate_linpack_fail (self, node):
        bench.util.mkdir_p(os.path.join(self.tests_dir, node))
        with open(os.path.join(self.tests_dir, node, 'linpack.out'), 'w') as fp:
            fp.write(LINPACK_FAIL)
