import bench.add
import hostlist
import os
import re
import shutil
import tempfile
import unittest


NODELIST_P = re.compile(r'(--nodelist|-w) *(|=) *([^ =]+) *\n')


class TestAddExecute (unittest.TestCase):

    def assertIsFile (self, path):
        assert os.path.isfile(path), '{0} does not exist'.format(path)

    def setUp (self):
        self.directory = tempfile.mkdtemp()
        self.nodes = set('node01{0:02}'.format(i) for i in xrange(1, 81))
        with open(os.path.join(self.directory, 'node_list'), 'w') as fp:
            for node in self.nodes:
                fp.write('{0}\n'.format(node))

    def tearDown (self):
        shutil.rmtree(self.directory)

    def test_execute_add_node_tests (self):
        bench.add.execute(self.directory, 'curc/topology.conf', add_node_tests=True)

        prefix = os.path.join(self.directory, 'node')
        scripts = set('{0}.job'.format(node) for node in self.nodes)
        self.assertEqual(
            set(os.listdir(prefix)),
            scripts,
        )
        for node in self.nodes:
            script = os.path.join(prefix, '{0}.job'.format(node))
            self.assertNotEqual(os.stat(script).st_size, 0)
            with open(script) as fp:
                match = NODELIST_P.search(fp.read())
            self.assertEqual(
                set(hostlist.expand_hostlist(match.group(3))),
                set((node, )),
            )

    def test_execute_alltoall_rack_tests (self):
        bench.add.execute(self.directory, 'curc/topology.conf', add_alltoall_rack_tests=True)

        prefix = os.path.join(self.directory, 'alltoall-rack')
        self.assertEqual(
            set(os.listdir(os.path.join(self.directory, 'alltoall-rack'))),
            set(('rack_01', )),
        )
        script = os.path.join(prefix, 'rack_01')
        self.assertNotEqual((os.stat(script)), 0)
        with open(script) as fp:
            match = NODELIST_P.search(fp.read())
        self.assertEqual(
            set(hostlist.expand_hostlist(match.group(3))),
            self.nodes,
        )

    def test_execute_alltoall_switch_tests (self):
        bench.add.execute(self.directory, 'curc/topology.conf', add_alltoall_switch_tests=True)

        prefix = os.path.join(self.directory, 'alltoall-switch')
        switches = set((
            'hpcf-ib-rack1-u43', 'hpcf-ib-rack1-u45',
            'hpcf-ib-rack1-u42', 'hpcf-ib-rack1-u44',
            'hpcf-ib-rack1-u46',
        ))
        self.assertEqual(
            set(os.listdir(prefix)),
            switches,
        )

        nodes = set()
        for switch in switches:
            script = os.path.join(prefix, switch)
            with open(script) as fp:
                match = NODELIST_P.search(fp.read())
            nodes |= set(hostlist.expand_hostlist(match.group(3)))
        self.assertEqual(nodes, self.nodes)

    def test_execute_alltoall_pair_tests (self):
        bench.add.execute(self.directory, 'curc/topology.conf', add_alltoall_pair_tests=True)

        prefix = os.path.join(self.directory, 'alltoall-pair')
        scripts = os.listdir(prefix)
        nodes = set()
        for script in scripts:
            with open(os.path.join(prefix, script)) as fp:
                match = NODELIST_P.search(fp.read())
            node_pair = set(hostlist.expand_hostlist(match.group(3)))
            self.assertEqual(len(node_pair), 2)
            nodes |= node_pair
        self.assertEqual(nodes, self.nodes)

    def test_execute_bandwidth_tests (self):
        bench.add.execute(self.directory, 'curc/topology.conf', add_bandwidth_tests=True)

        prefix = os.path.join(self.directory, 'bandwidth')
        scripts = os.listdir(prefix)
        nodes = set()
        for script in scripts:
            with open(os.path.join(prefix, script)) as fp:
                match = NODELIST_P.search(fp.read())
            node_pair = set(hostlist.expand_hostlist(match.group(3)))
            self.assertEqual(len(node_pair), 2)
            nodes |= node_pair
        self.assertEqual(nodes, self.nodes)
