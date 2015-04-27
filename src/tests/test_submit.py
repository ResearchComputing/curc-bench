import bench.submit
import mock
import os
import shutil
import tempfile
import unittest


def fake_Popen():
    popen = mock.Mock()
    popen.communicate = lambda: ('', '')
    return popen


class TestSubmit(unittest.TestCase):

    def setUp (self):
        self.prefix = tempfile.mkdtemp()
        self.test_dir = tempfile.mkdtemp(dir=self.prefix)
        self.script = os.path.join(self.test_dir, '{0}.job'.format(os.path.basename(self.test_dir)))
        print self.script
        with open(self.script, 'w') as fp:
            pass # just create the file
        assert os.path.exists(self.script)


    def tearDown (self):
        shutil.rmtree(self.prefix)

    @mock.patch('bench.submit.bench.slurm.subprocess.Popen',
                return_value=fake_Popen())

    def test_submit(self, arg1):
        new_index = bench.submit.submit(
            self.prefix,
            index=0, pause=None, reservation='PM', qos='High', account='Account')

        #Did it find the file?
        self.assertEqual(1, new_index)
        #Arguments correct?
        call_args = arg1.call_args_list[0][0][0]
        self.assertTrue('sbatch' in call_args)
        self.assertTrue(self.script in call_args)
        self.assertTrue('--reservation' in call_args)
        self.assertTrue('PM' in call_args)
        self.assertTrue('--qos' in call_args)
        self.assertTrue('High' in call_args)
        self.assertTrue('--account' in call_args)
        self.assertTrue('Account' in call_args)

    @mock.patch('bench.submit.bench.slurm.subprocess.Popen',
                return_value=fake_Popen())

    def test_submit2(self, arg1):
        new_index = bench.submit.submit(
            self.prefix,
            index=0, pause=None, reservation=None, qos=None, account=None)

        #Did it find the file?
        self.assertEqual(1, new_index)
        #Arguments correct?
        call_args = arg1.call_args_list[0][0][0]
        self.assertTrue('sbatch' in call_args)
        self.assertTrue(self.script in call_args)
