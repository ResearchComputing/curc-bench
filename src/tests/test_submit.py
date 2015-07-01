import bench.submit
import mock
import os
import shutil
import tempfile
import unittest


def fake_Popen():
    popen = mock.Mock()
    popen.communicate = lambda: ('', '')
    popen.returncode = 0
    return popen


class TestSubmit(unittest.TestCase):

    def setUp (self):
        self.prefix = tempfile.mkdtemp()

        self.tests_dir = os.path.join(self.prefix, 'tests')
        os.mkdir(self.tests_dir)

    def _add_test (self, node):
        test_dir = os.path.join(self.tests_dir, node)
        os.mkdir(test_dir)
        script_basename = '{0}.job'.format(os.path.basename(test_dir))
        script = os.path.join(test_dir, script_basename)
        with open(script, 'w') as fp:
            pass # just create the file
        with open(os.path.join(test_dir, 'node_list'), 'w') as fp:
            fp.write('{0}\n'.format(node))
        return test_dir

    def _add_good_node (self, node):
        with open(os.path.join(self.prefix, 'good_nodes'), 'a') as fp:
            fp.write('{0}\n'.format(node))

    def _add_bad_node (self, node):
        with open(os.path.join(self.prefix, 'bad_nodes'), 'a') as fp:
            fp.write('{0}\n'.format(node))

    def _add_not_tested (self, node):
        with open(os.path.join(self.prefix, 'not_tested'), 'a') as fp:
            fp.write('{0}\n'.format(node))

    def tearDown (self):
        if os.path.exists(self.prefix):
            shutil.rmtree(self.prefix)

    @mock.patch('bench.submit.bench.slurm.subprocess.Popen',
                return_value=fake_Popen())
    def test_missing_tests_dir (self, arg1):
        shutil.rmtree(self.tests_dir)
        new_index = bench.submit.submit(
            self.prefix,
            index=0, pause=None, reservation='PM', qos='High', account='Account')
        self.assertEqual(new_index, 0)
        self.assertEqual(arg1.call_args_list, [])

    @mock.patch('bench.submit.bench.slurm.subprocess.Popen',
                return_value=fake_Popen())
    def test_missing_script (self, arg1):
        test_dir = self._add_test('tnode1')
        os.remove(os.path.join(test_dir, '{0}.job'.format('tnode1')))
        new_index = bench.submit.submit(
            self.prefix,
            index=0, pause=None, reservation='PM', qos='High', account='Account')
        self.assertEqual(new_index, 0)
        self.assertEqual(arg1.call_args_list, [])

    @mock.patch('bench.submit.bench.slurm.subprocess.Popen',
                return_value=fake_Popen())
    def test_submit(self, arg1):
        test_dir = self._add_test('tnode1')
        script = os.path.join(test_dir, '{0}.job'.format('tnode1'))
        new_index = bench.submit.submit(
            self.prefix,
            index=0, pause=None, reservation='PM', qos='High', account='Account')

        #Did it find the file?
        self.assertEqual(1, new_index)
        #Arguments correct?
        call_args = arg1.call_args_list[0][0][0]
        self.assertTrue('sbatch' in call_args)
        self.assertTrue(script in call_args)
        self.assertTrue('--reservation' in call_args)
        self.assertTrue('PM' in call_args)
        self.assertTrue('--qos' in call_args)
        self.assertTrue('High' in call_args)
        self.assertTrue('--account' in call_args)
        self.assertTrue('Account' in call_args)

    @mock.patch('bench.submit.bench.slurm.subprocess.Popen',
                return_value=fake_Popen())
    def test_good_nodes (self, popen):
        self._add_test('tnode1')
        self._add_test('tnode2')
        self._add_test('tnode3')
        self._add_good_node('tnode1')
        self._add_good_node('tnode3')
        new_index = bench.submit.submit(self.prefix, good_nodes=True)
        self.assertEqual(new_index, 2)
        self.assertEqual(len(popen.call_args_list), 2)

    @mock.patch('bench.submit.bench.slurm.subprocess.Popen',
                return_value=fake_Popen())
    def test_bad_nodes (self, popen):
        self._add_test('tnode1')
        self._add_test('tnode2')
        self._add_test('tnode3')
        self._add_bad_node('tnode2')
        new_index = bench.submit.submit(self.prefix, bad_nodes=True)
        self.assertEqual(new_index, 1)
        self.assertEqual(len(popen.call_args_list), 1)

    @mock.patch('bench.submit.bench.slurm.subprocess.Popen',
                return_value=fake_Popen())
    def test_not_tested (self, popen):
        self._add_test('tnode1')
        self._add_test('tnode2')
        self._add_test('tnode3')
        self._add_not_tested('tnode3')
        new_index = bench.submit.submit(self.prefix, not_tested=True)
        self.assertEqual(new_index, 1)
        self.assertEqual(len(popen.call_args_list), 1)

    @mock.patch('bench.submit.bench.slurm.subprocess.Popen',
                return_value=fake_Popen())
    def test_good_nodes_missing_file (self, popen):
        self._add_test('tnode1')
        self._add_test('tnode2')
        self._add_test('tnode3')
        new_index = bench.submit.submit(self.prefix, good_nodes=True)
        self.assertEqual(new_index, 0)
        self.assertEqual(len(popen.call_args_list), 0)

    @mock.patch('bench.submit.bench.slurm.subprocess.Popen',
                return_value=fake_Popen())
    def test_bad_nodes_missing_file (self, popen):
        self._add_test('tnode1')
        self._add_test('tnode2')
        self._add_test('tnode3')
        new_index = bench.submit.submit(self.prefix, bad_nodes=True)
        self.assertEqual(new_index, 0)
        self.assertEqual(len(popen.call_args_list), 0)


    @mock.patch('bench.submit.bench.slurm.subprocess.Popen',
                return_value=fake_Popen())
    def test_not_tested_missing_file (self, popen):
        self._add_test('tnode1')
        self._add_test('tnode2')
        self._add_test('tnode3')
        new_index = bench.submit.submit(self.prefix, not_tested=True)
        self.assertEqual(new_index, 0)
        self.assertEqual(len(popen.call_args_list), 0)

