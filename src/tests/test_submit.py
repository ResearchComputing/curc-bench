import bench.submit
import mock
import os
import shutil
import tempfile
import unittest


def fake_subprocess(cmd, shell):
    subprocess = mock.Mock()
    subprocess.check_output = mock.Mock(return_value=([cmd], shell))
    return subprocess


class TestSubmit(unittest.TestCase):

    def setUp (self):
        self.directory = tempfile.mkdtemp()
        self.folder = tempfile.mkdtemp(dir=self.directory)
        self.file = tempfile.NamedTemporaryFile(prefix='script_10', dir=self.folder)

    def tearDown (self):
        shutil.rmtree(self.folder)
        shutil.rmtree(self.directory)

    @mock.patch('bench.submit.subprocess.check_output',
                return_value=fake_subprocess('script_10', True))
    def test_submit(self, arg1):
        index = 0
        pause = None
        reservation = 'PM'
        qos = "High"
        account = "Account"
        new_index = bench.submit.submit(self.directory, self.folder,
                                        index, pause, reservation, qos, account)

        #Did it find the file?
        self.assertEqual(1, new_index)
        #Arguments correct?
        self.assertTrue('sbatch ' in str(arg1.call_args_list))
        self.assertTrue(' script_10' in str(arg1.call_args_list))
        self.assertTrue(' --reservation=PM ' in str(arg1.call_args_list))
        self.assertTrue(' --qos=High ' in str(arg1.call_args_list))
        self.assertTrue(' --account=Account ' in str(arg1.call_args_list))
        #Shell==True?
        self.assertEqual(True, arg1.call_args_list[0][1]['shell'])

    @mock.patch('bench.submit.subprocess.check_output',
                return_value=fake_subprocess('script_10', True))
    def test_submit2(self, arg1):
        index = 0
        pause = None
        reservation = None
        qos = None
        account = None
        new_index = bench.submit.submit(self.directory, self.folder,
                                        index, pause, reservation, qos, account)

        #Did it find the file?
        self.assertEqual(1, new_index)
        #Arguments correct?
        self.assertTrue('sbatch script_10' in str(arg1.call_args_list))
        #Shell==True?
        self.assertEqual(True, arg1.call_args_list[0][1]['shell'])
