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


def fake_node (node_dict):
    node = mock.Mock()
    for node_name, node_ in node_dict.items():
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
NODES = set('tnode01{0:02}'.format(i) for i in range(1, 81))

@mock.patch.dict(bench.conf.node_conf.config, {'nodes' : 'tnode01[01-03]',
                                                'modules' : ['intel'],
                                                'linpack_path' : '/fake/linpack.so',
                                                'stream_path' : '/fake/stream.so',
                                                'stream_copy' : 88000.0,
                                                'stream_scale' : 89000.0,
                                                'stream_add' : 91000.0,
                                                'stream_triad' : 92000.0,
                                                'linpack_averages' : {(5000, 5000, 4): 380.0,
                                                                      (10000, 10000, 4): 580.0,
                                                                      (20000, 20000, 4): 670.0,
                                                                      (25000, 25000, 4): 640.0 }})
@mock.patch.dict(bench.conf.bandwidth_conf.config, {'nodes' : 'tnode01[01-08,11-18]',
                                                'modules' : ['intel/17.4', 'impi/17.3'],
                                                'osu_bw_path' : '/fake/osu_bw.so',
                                                'osu_bandwidths' : {
                                                    4194304: 10000.0,
                                                    1048576: 10000.0,
                                                    262144: 10000.0,
                                                    65536: 6000.0,
                                                }})
@mock.patch.dict(bench.conf.alltoall_conf.config, {'osu_a2a_path' : '/fake/osu_alltoall.so',
                                                'modules' : ['intel/17.4', 'impi/17.3'],
                                                'nodes' : 'tnode01[01-08,11-18]',
                                                'latency_factor': 1.55,
                                                'osu_latencies' : { 2:13613.5219632, 3:28375.5187868,
                                                                       4:43137.5156105, 5:57899.5124341,
                                                                       6:72661.5092577, 7:87423.5060814,
                                                                       8:102185.502905, 9:116947.499729,
                                                                       10:131709.496552, 11:146471.493376,
                                                                       12:161233.4902, 13:175995.487023,
                                                                       14:190757.483847, 15:205519.480671,
                                                                       16:220281.477494, 17:235043.474318,
                                                                       18:249805.471141, 19:264567.467965,
                                                                       20:279329.464789, 21:294091.461612,
                                                                       22:308853.458436, 23:323615.45526,
                                                                       24:338377.452083, 25:353139.448907,
                                                                       26:367901.445731, 27:382663.442554,
                                                                       28:397425.439378, 29:412187.436202,
                                                                       30:426949.433025, 31:441711.429849,
                                                                       32:456473.426672, 33:471235.423496,
                                                                       34:753806.42032, 35:753806.417143,
                                                                       36:753806.413967, 37:753806.410791,
                                                                       38:753806.407614, 39:753806.404438,
                                                                       40:753806.401262, 50:456062.014488,
                                                                       51:522754.035136, 52:589446.055784,
                                                                       53:656138.076432, 54:722830.09708,
                                                                       55:789522.117728, 56:856214.138376,
                                                                       57:922906.159024, 58:989598.179672,
                                                                       59:1056290.20032, 60:1122982.22097,
                                                                       61:1189674.24162, 62:1256366.26226,
                                                                       63:1323058.28291, 64:1389750.30356,
                                                                       65:1456442.32421, 66:1523134.34486,
                                                                       67:1589826.3655, 68:1656518.38615,
                                                                       69:1723210.4068, 70:1789902.42745,
                                                                       71:1856594.4481, 72:1923286.46874,
                                                                       73:1989978.48939, 74:2056670.51004,
                                                                       75:2123362.53069, 76:2190054.55134,
                                                                       77:2256746.57198, 78:2323438.59263,
                                                                       79:2390130.61328, 80:2456822.63393, }})

@mock.patch.dict(bench.conf.alltoall_conf.config, {'Switch': {'switch1' : 'tnode01[01-04]',
                                                'switch2' : 'tnode01[05-08]',
                                                'switch3' : 'tnode01[11-14]',
                                                'switch4' : 'tnode01[15-18]'}})
@mock.patch.dict(bench.conf.alltoall_conf.config, {'Rack': {'rack1' : 'tnode01[01-08]',
                                                'rack2' : 'tnode01[11-18]'}})
@mock.patch('bench.create.bench.util.pyslurm.node',
            return_value=fake_node(dict((node, {'state': 'fake_state', 'name' : node}) for node in NODES)))
class TestAdd(unittest.TestCase):

    def assertIsFile (self, path):
        assert os.path.isfile(path), '{0} does not exist'.format(path)

    def setUp (self):
        self.directory = tempfile.mkdtemp()
        self.nodes = set('tnode01{0:02}'.format(i) for i in range(1, 81))
        bench.util.write_node_list(os.path.join(self.directory, 'node_list'),
                                   self.nodes)
        self.bench_node_list = os.path.join(self.directory, 'node_list')

    def tearDown (self):
        shutil.rmtree(self.directory)


    def test_node_tests (self, _):
        node_test = bench.tests.node_test.NodeTest("node")
        node_test.Add.execute(self.directory)

        #Test that correct nodelist is written out for node test
        with open(os.path.join(self.directory, 'node', 'node_list'), 'r') as nodefile:
            nodes = nodefile.read()
            self.assertEqual(nodes, 'tnode0101\ntnode0102\ntnode0103\n')
            nodefile.close()

        #Test for test executables and directives in job script
        with open(os.path.join(self.directory, 'node', 'tests', 'tnode0101', 'tnode0101.job'), 'r') as jobfile:
            script = jobfile.read()
            self.assertIn('/fake/linpack.so', script)
            self.assertIn('/fake/stream.so', script)
            self.assertIn('intel', script)
            self.assertIn('#SBATCH --nodes=1', script)
            self.assertIn('#!/bin/bash', script)
            jobfile.close()


    def test_bw_tests (self, _):
        bw_test = bench.tests.bandwidth_test.BandwidthTest("bandwidth")
        bw_test.Add.execute(self.directory)
        #Test that correct nodelist is written out for node test
        bw_nodes = ''
        for jj in range(0,2):
            for ii in range(1,9):
                bw_nodes += 'tnode01{jj}{ii}\n'.format(ii=ii, jj=jj)

        with open(os.path.join(self.directory, 'bandwidth', 'node_list'), 'r') as nodefile:
            nodes = nodefile.read()
            self.assertEqual(nodes, bw_nodes)
            nodefile.close()

        #Test for test executables and directives in job script
        with open(os.path.join(self.directory, 'bandwidth', 'tests',
                'tnode0101,tnode0102', 'tnode0101,tnode0102.job'), 'r') as jobfile:
            script = jobfile.read()
            self.assertIn('/fake/osu_bw.so', script)
            self.assertIn('intel/17.4 impi/17.3', script)
            self.assertIn('#SBATCH --nodelist=tnode0101,tnode0102', script)
            self.assertIn('#!/bin/bash', script)
            jobfile.close()

    def test_alltoall_tests (self, _):
        a2a_nodes = ''
        a2a_rack2 = []
        for ii in range(1,9):
            a2a_rack2.append('tnode011{ii}'.format(ii=ii))
        a2a_rack = ','.join(a2a_rack2)

        for jj in range(0,2):
            for ii in range(1,9):
                a2a_nodes += 'tnode01{jj}{ii}\n'.format(ii=ii, jj=jj)

        test_scripts = {}
        test_scripts['pair'] = os.path.join('tnode0111,tnode0112', 'tnode0111,tnode0112.job')
        test_scripts['switch'] = os.path.join('switch1', 'switch1.job')
        test_scripts['rack'] = os.path.join('rack2', 'rack2.job')

        test_nodelists = {}
        test_nodelists['pair'] = '#SBATCH --nodelist=tnode0111,tnode0112'
        test_nodelists['switch'] = '#SBATCH --nodelist=tnode0101,tnode0102,tnode0103,tnode0104'
        test_nodelists['rack'] = a2a_rack

        for testname in ['pair', 'switch', 'rack']:
            test = bench.tests.alltoall_tests.AllToAllTest("alltoall-{test}".format(test=testname))
            test.Add.execute(self.directory)

            #Test that correct nodelist is written out for node test
            with open(os.path.join(self.directory, "alltoall-{test}".format(test=testname), 'node_list'), 'r') as nodefile:
                nodes = nodefile.read()
                self.assertEqual(nodes, a2a_nodes)
                nodefile.close()

            #Test for test executables and directives in job script
            with open(os.path.join(self.directory, "alltoall-{test}".format(test=testname),
                                'tests', test_scripts[testname]), 'r') as testfile:
                script = testfile.read()
                self.assertIn('/fake/osu_alltoall.so', script)
                self.assertIn('intel/17.4 impi/17.3', script)
                self.assertIn(test_nodelists[testname], script)
                self.assertIn('#!/bin/bash', script)
                testfile.close()





















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
