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


class TestProcessExecute (unittest.TestCase):

    def setUp (self):
        self.directory = tempfile.mkdtemp()
        self.prefix = os.path.join(self.directory, 'node')
        self.tests_dir = os.path.join(self, self.prefix, 'tests')
        bench.util.mkdir_p(self.tests_dir)
        self.nodes = set('node01{0:02}'.format(i) for i in xrange(1, 81))
        self.good_nodes = set(sorted(self.nodes)[:10])
        self.bad_nodes = set(sorted(self.nodes)[-10:])
        self.assertEqual(len(self.good_nodes & self.bad_nodes), 0)
        self.not_tested = self.nodes - (self.good_nodes | self.bad_nodes)
        with open(os.path.join(self.directory, 'node_list'), 'w') as fp:
            for node in self.nodes:
                fp.write('{0}\n'.format(node))
        for node in self.good_nodes:
            self._populate_node_list(node)
            self._populate_stream_pass(node)
            self._populate_linpack_pass(node)
        for node in self.bad_nodes:
            self._populate_node_list(node)
            self._populate_stream_fail(node)
            self._populate_linpack_fail(node)

    def tearDown (self):
        shutil.rmtree(self.directory)

    def read_node_list (self, path):
        with open(path) as fp:
            return set(fp.read().splitlines())
    
    def test_execute_node_tests (self):
        bench.process.execute(self.directory, node_tests=True)
        good_nodes = self.read_node_list(
            os.path.join(self.prefix, 'good_nodes'))
        bad_nodes = self.read_node_list(
            os.path.join(self.prefix, 'bad_nodes'))
        not_tested = self.read_node_list(
            os.path.join(self.prefix, 'not_tested'))
        self.assertEqual(good_nodes, self.good_nodes)
        self.assertEqual(bad_nodes, self.bad_nodes)
        self.assertEqual(not_tested, self.not_tested)
    
    def test_execute_node_tests_missing_stream (self):
        missing_stream_nodes = set(sorted(self.good_nodes)[:5])
        for node in missing_stream_nodes:
            self._remove_stream(node)
        bench.process.execute(self.directory, node_tests=True)
        good_nodes = self.read_node_list(
            os.path.join(self.prefix, 'good_nodes'))
        bad_nodes = self.read_node_list(
            os.path.join(self.prefix, 'bad_nodes'))
        not_tested = self.read_node_list(
            os.path.join(self.prefix, 'not_tested'))
        self.assertEqual(good_nodes, self.good_nodes - missing_stream_nodes)
        self.assertEqual(bad_nodes, self.bad_nodes)
        self.assertEqual(not_tested, self.not_tested | missing_stream_nodes)
    
    def test_execute_node_tests_missing_linpack (self):
        missing_linpack_nodes = set(sorted(self.good_nodes)[-5:])
        for node in missing_linpack_nodes:
            self._remove_linpack(node)
        bench.process.execute(self.directory, node_tests=True)
        good_nodes = self.read_node_list(
            os.path.join(self.prefix, 'good_nodes'))
        bad_nodes = self.read_node_list(
            os.path.join(self.prefix, 'bad_nodes'))
        not_tested = self.read_node_list(
            os.path.join(self.prefix, 'not_tested'))
        self.assertEqual(good_nodes, self.good_nodes - missing_linpack_nodes)
        self.assertEqual(bad_nodes, self.bad_nodes)
        self.assertEqual(not_tested, self.not_tested | missing_linpack_nodes)
    
    def test_execute_node_tests_corrupt_stream (self):
        corrupt_stream_nodes = set(sorted(self.good_nodes)[:5])
        for node in corrupt_stream_nodes:
            self._corrupt_stream(node)
        bench.process.execute(self.directory, node_tests=True)
        good_nodes = self.read_node_list(
            os.path.join(self.prefix, 'good_nodes'))
        bad_nodes = self.read_node_list(
            os.path.join(self.prefix, 'bad_nodes'))
        not_tested = self.read_node_list(
            os.path.join(self.prefix, 'not_tested'))
        self.assertEqual(good_nodes, self.good_nodes - corrupt_stream_nodes)
        self.assertEqual(bad_nodes, self.bad_nodes)
        self.assertEqual(not_tested, self.not_tested | corrupt_stream_nodes)
    
    def test_execute_node_tests_corrupt_linpack (self):
        corrupt_linpack_nodes = set(sorted(self.good_nodes)[-5:])
        for node in corrupt_linpack_nodes:
            self._corrupt_linpack(node)
        bench.process.execute(self.directory, node_tests=True)
        good_nodes = self.read_node_list(
            os.path.join(self.prefix, 'good_nodes'))
        bad_nodes = self.read_node_list(
            os.path.join(self.prefix, 'bad_nodes'))
        not_tested = self.read_node_list(
            os.path.join(self.prefix, 'not_tested'))
        self.assertEqual(good_nodes, self.good_nodes - corrupt_linpack_nodes)
        self.assertEqual(bad_nodes, self.bad_nodes)
        self.assertEqual(not_tested, self.not_tested | corrupt_linpack_nodes)

    def _populate_node_list (self, node):
        bench.util.mkdir_p(os.path.join(self.tests_dir, node))
        print os.path.join(self.tests_dir, node, 'node_list')
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
