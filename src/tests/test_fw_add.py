import bench.framework
import bench.tests.node_test
import bench.tests.bandwidth_test
import bench.tests.alltoall_tests
import bench.tests.ior
import bench.util
import hostlist
import mock
import os
import pkg_resources
import re
import shutil
import tempfile
import unittest


TOPOLOGY_FILE = pkg_resources.resource_filename(__name__, 'topology.conf')


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


NODELIST_P = re.compile(r'(--nodelist|-w) *(|=) *([^ =]+) *\n')
NODES = set('tnode01{0:02}'.format(i) for i in xrange(1, 81))


class TestAdd(unittest.TestCase):

    def assertIsFile (self, path):
        assert os.path.isfile(path), '{0} does not exist'.format(path)

    def setUp (self):
        self.directory = tempfile.mkdtemp()
        self.nodes = set('tnode01{0:02}'.format(i) for i in xrange(1, 81))
        bench.util.write_node_list(os.path.join(self.directory, 'node_list'),
                                   self.nodes)
        self.bench_node_list = os.path.join(self.directory, 'node_list')

    def tearDown (self):
        shutil.rmtree(self.directory)


    @mock.patch.dict(bench.configuration.config, {'node': {'nodes' : 'tnode01[01-03]',
                                                    'linpack' : '/fake/linpack.so',
                                                    'stream' : '/fake/stream.so'}})
    @mock.patch('bench.create.bench.util.pyslurm.node',
                return_value=fake_node(dict((node, {'state': 'fake_state', 'name' : node}) for node in NODES)))
    def test_node_tests (self, _):

        node_test = bench.tests.node_test.NodeTest("node")
        node_test.Add.execute(self.directory)

        #Test that correct nodelist is written out for node test
        self.assertEqual(open(os.path.join(self.directory, 'node', 'node_list')).read(), 'tnode0101\ntnode0102\ntnode0103\n')

        #Test for test executables and directives in job script
        script = open(os.path.join(self.directory, 'node', 'tests', 'tnode0101', 'tnode0101.job')).read()
        self.assertIn('/fake/linpack.so', script)
        self.assertIn('/fake/stream.so', script)
        self.assertIn('#SBATCH --nodes=1', script)
        self.assertIn('#!/bin/bash', script)


    @mock.patch.dict(bench.configuration.config, {'bandwidth': {'nodes' : 'tnode01[01-08]',
                                                    'osu' : '/fake/osu_bw.so'}})
    @mock.patch.dict(bench.configuration.config, {'Switch': {'switch1' : 'tnode01[01-04]',
                                                    'switch2' : 'tnode01[05-08]'}})
    @mock.patch('bench.create.bench.util.pyslurm.node',
                return_value=fake_node(dict((node, {'state': 'fake_state', 'name' : node}) for node in NODES)))
    def test_bw_tests (self, _):

        bw_test = bench.tests.bandwidth_test.BandwidthTest("bandwidth")
        bw_test.Add.execute(self.directory)
        #Test that correct nodelist is written out for node test
        bw_nodes = ''
        for ii in range(1,9):
            bw_nodes += 'tnode01{0:02}\n'.format(ii)
        #print("BW NODES = ", bw_nodes)
        self.assertEqual(open(os.path.join(self.directory, 'bandwidth', 'node_list')).read(), bw_nodes)

        #Test for test executables and directives in job script
        script = open(os.path.join(self.directory, 'bandwidth', 'tests',
                            'tnode0101,tnode0102', 'tnode0101,tnode0102.job')).read()
        self.assertIn('/fake/osu_bw.so', script)
        self.assertIn('#SBATCH --nodelist=tnode0101,tnode0102', script)
        self.assertIn('#!/bin/bash', script)

    #
    # @mock.patch('bench.create.bench.util.pyslurm.node',
    #             return_value=fake_node(dict((node, {}) for node in NODES)))
    # def test_alltoall_rack_tests (self, _):
    #     bench.add.execute(self.directory, TOPOLOGY_FILE, alltoall_rack_tests=True)
    #
    #     prefix = os.path.join(self.directory, 'alltoall-rack', 'tests')
    #     self.assertEqual(
    #         set(os.listdir(prefix)),
    #         set(('rack_01', )),
    #     )
    #     script = os.path.join(prefix, 'rack_01', 'rack_01.job')
    #     self.assertNotEqual((os.stat(script)), 0)
    #     with open(script) as fp:
    #         match = NODELIST_P.search(fp.read())
    #     self.assertEqual(
    #         set(hostlist.expand_hostlist(match.group(3))),
    #         self.nodes,
    #     )
    #
    # @mock.patch('bench.create.bench.util.pyslurm.node',
    #             return_value=fake_node(dict((node, {}) for node in NODES)))
    # def test_alltoall_switch_tests (self, _):
    #     self.nodes = NODES
    #     bench.util.write_node_list(os.path.join(self.directory, 'node_list'),
    #                                self.nodes)
    #     bench.add.execute(self.directory, TOPOLOGY_FILE, alltoall_switch_tests=True)
    #
    #     prefix = os.path.join(self.directory, 'alltoall-switch', 'tests')
    #     switches = set((
    #         'hpcf-ib-rack1-u43', 'hpcf-ib-rack1-u45',
    #         'hpcf-ib-rack1-u42', 'hpcf-ib-rack1-u44',
    #         'hpcf-ib-rack1-u46',
    #     ))
    #     self.assertEqual(
    #         set(os.listdir(prefix)),
    #         switches,
    #     )
    #
    #     nodes = set()
    #     for switch in switches:
    #         script = os.path.join(prefix, switch, '{0}.job'.format(switch))
    #         with open(script) as fp:
    #             match = NODELIST_P.search(fp.read())
    #         nodes |= set(hostlist.expand_hostlist(match.group(3)))
    #     self.assertEqual(nodes, self.nodes)
    #
    # @mock.patch('bench.create.bench.util.pyslurm.node',
    #             return_value=fake_node(dict((node, {}) for node in NODES)))
    # def test_alltoall_pair_tests (self, _):
    #     bench.add.execute(self.directory, TOPOLOGY_FILE, alltoall_pair_tests=True)
    #
    #     prefix = os.path.join(self.directory, 'alltoall-pair', 'tests')
    #     script_dirs = os.listdir(prefix)
    #     nodes = set()
    #     for script_dir in script_dirs:
    #         with open(os.path.join(prefix, script_dir, '{0}.job'.format(script_dir))) as fp:
    #             match = NODELIST_P.search(fp.read())
    #         node_pair = set(hostlist.expand_hostlist(match.group(3)))
    #         self.assertEqual(len(node_pair), 2)
    #         nodes |= node_pair
    #     self.assertEqual(nodes, self.nodes)
    #
    # @mock.patch('bench.create.bench.util.pyslurm.node',
    #             return_value=fake_node(dict((node, {}) for node in NODES)))
    # def test_bandwidth_tests (self, _):
    #     bench.add.execute(self.directory, TOPOLOGY_FILE, bandwidth_tests=True)
    #
    #     tests_dir = os.path.join(self.directory, 'bandwidth', 'tests')
    #     nodes = set()
    #     for test in os.listdir(tests_dir):
    #         script = os.path.join(tests_dir, test, '{0}.job'.format(test))
    #         with open(script) as fp:
    #             match = NODELIST_P.search(fp.read())
    #         node_pair = set(hostlist.expand_hostlist(match.group(3)))
    #         self.assertEqual(len(node_pair), 2)
    #         nodes |= node_pair
    #     self.assertEqual(nodes, self.nodes)
    #
    # @mock.patch('bench.create.bench.util.pyslurm.node',
    #             return_value=fake_node(dict((node, {}) for node in NODES)))
    # def test_include_file (self, _):
    #     pass_nodes = os.path.join(self.directory, 'pass_nodes')
    #     with open(pass_nodes, 'w') as fp:
    #         for node in ['tnode0101', 'tnode0102', 'nonode0101']:
    #             fp.write('{0}\n'.format(node))
    #
    #     bench.add.execute(
    #         self.directory,
    #         topology_file=TOPOLOGY_FILE,
    #         node_tests=True,
    #         include_files=[pass_nodes],
    #     )
    #
    #     tests_dir = os.path.join(self.directory, 'node', 'tests')
    #     expected_tests = set(['tnode0101', 'tnode0102'])
    #     self.assertEqual(
    #         set(os.listdir(tests_dir)),
    #         expected_tests,
    #     )
    #     for node in expected_tests:
    #         script = os.path.join(tests_dir, node, '{0}.job'.format(node))
    #         self.assertNotEqual(os.stat(script).st_size, 0)
    #         with open(script) as fp:
    #             match = NODELIST_P.search(fp.read())
    #         self.assertEqual(
    #             set(hostlist.expand_hostlist(match.group(3))),
    #             set((node, )),
    #         )
    #
    # @mock.patch('bench.create.bench.util.pyslurm.node',
    #             return_value=fake_node(dict((node, {}) for node in NODES)))
    # def test_exclude_file (self, _):
    #     fail_nodes = os.path.join(self.directory, 'fail_nodes')
    #     with open(fail_nodes, 'w') as fp:
    #         for node in ['tnode0101', 'tnode0102', 'tnode0208', 'nonode0101']:
    #             fp.write('{0}\n'.format(node))
    #
    #     bench.add.execute(
    #         self.directory,
    #         topology_file=TOPOLOGY_FILE,
    #         node_tests=True,
    #         exclude_files=[fail_nodes],
    #     )
    #
    #     tests_dir = os.path.join(self.directory, 'node', 'tests')
    #     expected_tests = set(self.nodes) - set(['tnode0101', 'tnode0102', 'tnode0208', 'nonode0101'])
    #     self.assertEqual(
    #         set(os.listdir(tests_dir)),
    #         expected_tests,
    #     )
    #     for node in expected_tests:
    #         script = os.path.join(tests_dir, node, '{0}.job'.format(node))
    #         self.assertNotEqual(os.stat(script).st_size, 0)
    #         with open(script) as fp:
    #             match = NODELIST_P.search(fp.read())
    #         self.assertEqual(
    #             set(hostlist.expand_hostlist(match.group(3))),
    #             set((node, )),
    #         )
    #
    # @mock.patch('bench.create.bench.util.pyslurm.node',
    #             return_value=fake_node(dict((node, {}) for node in NODES)))
    # @mock.patch('bench.add.bench.util.pyslurm.reservation',
    #             return_value=fake_reservation({'res1': {'node_list': 'tnode0101,tnode0103'}}))
    # def test_include_reservation (self, _n, _r):
    #     bench.add.execute(
    #         self.directory,
    #         topology_file=TOPOLOGY_FILE,
    #         node_tests=True,
    #         include_reservations=['res1'],
    #     )
    #
    #     node_list = os.path.join(self.directory, 'node', 'node_list')
    #     self.assertTrue(os.path.exists(node_list), node_list)
    #     self.assertEqual(open(node_list).read(), 'tnode0101\ntnode0103\n')
    #
    # @mock.patch('bench.create.bench.util.pyslurm.node',
    #             return_value=fake_node(dict((node, {}) for node in NODES)))
    # @mock.patch('bench.add.bench.util.pyslurm.reservation',
    #             return_value=fake_reservation({'res1': {'node_list': 'tnode0101,tnode0103'}}))
    # def test_include_reservation_include_nodes (self, _n, _r):
    #     bench.add.execute(
    #         self.directory,
    #         topology_file=TOPOLOGY_FILE,
    #         node_tests=True,
    #         include_reservations=['res1'],
    #         include_nodes=['tnode0102'],
    #     )
    #     node_list = os.path.join(self.directory, 'node', 'node_list')
    #     self.assertTrue(os.path.exists(node_list), node_list)
    #     self.assertEqual(open(node_list).read(), 'tnode0101\ntnode0102\ntnode0103\n')
    #
    # @mock.patch('bench.create.bench.util.pyslurm.node',
    #             return_value=fake_node(dict((node, {}) for node in NODES)))
    # @mock.patch('bench.add.bench.util.pyslurm.reservation',
    #             return_value=fake_reservation({'res1': {'node_list': 'tnode0101,tnode0103'}}))
    # def test_include_reservation_exclude_nodes (self, _n, _r):
    #     bench.add.execute(
    #         self.directory,
    #         topology_file=TOPOLOGY_FILE,
    #         node_tests=True,
    #         include_reservations=['res1'],
    #         exclude_nodes=['tnode0101'],
    #     )
    #
    #     node_list = os.path.join(self.directory, 'node', 'node_list')
    #     self.assertTrue(os.path.exists(node_list), node_list)
    #     self.assertEqual(open(node_list).read(), 'tnode0103\n')
    #
    # @mock.patch('bench.create.bench.util.pyslurm.node',
    #             return_value=fake_node(dict((node, {}) for node in NODES)))
    # @mock.patch('bench.add.bench.util.pyslurm.reservation',
    #             return_value=fake_reservation({'res1': {'node_list': 'tnode0101,tnode0103'}}))
    # def test_exclude_reservation (self, _n, _r):
    #     bench.add.execute(
    #         self.directory,
    #         topology_file=TOPOLOGY_FILE,
    #         node_tests=True,
    #         exclude_reservations=['res1'],
    #     )
    #     node_list = os.path.join(self.directory, 'node', 'node_list')
    #     self.assertTrue(os.path.exists(node_list), node_list)
    #     self.assertEqual(open(node_list).read(), 'tnode0102\n')
    #
    # @mock.patch('bench.create.bench.util.pyslurm.node',
    #             return_value=fake_node(dict((node, {}) for node in NODES)))
    # @mock.patch('bench.add.bench.util.pyslurm.reservation',
    #             return_value=fake_reservation({'res1': {'node_list': 'tnode0101,tnode0103'}}))
    # def test_exclude_reservation_include_nodes (self, _n, _r):
    #     bench.add.execute(
    #         self.directory,
    #         topology_file=TOPOLOGY_FILE,
    #         node_tests=True,
    #         exclude_reservations=['res1'],
    #         include_nodes=['tnode0101'],
    #     )
    #     node_list = os.path.join(self.directory, 'node', 'node_list')
    #     self.assertTrue(os.path.exists(node_list), node_list)
    #     self.assertEqual(open(node_list).read(), '')
    #
    # @mock.patch('bench.create.bench.util.pyslurm.node',
    #             return_value=fake_node(dict((node, {}) for node in NODES)))
    # @mock.patch('bench.add.bench.util.pyslurm.reservation',
    #             return_value=fake_reservation({'res1': {'node_list': 'tnode0101,tnode0103'}}))
    # def test_exclude_reservation_exclude_nodes (self, _n, _r):
    #     bench.add.execute(
    #         self.directory,
    #         topology_file=TOPOLOGY_FILE,
    #         node_tests=True,
    #         exclude_reservations=['res1'],
    #         exclude_nodes=['tnode0102'],
    #     )
    #     node_list = os.path.join(self.directory, 'node', 'node_list')
    #     self.assertTrue(os.path.exists(node_list), node_list)
    #     self.assertEqual(open(node_list).read(), '')
