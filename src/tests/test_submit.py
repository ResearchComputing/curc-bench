import bench.submit
import mock
import os
import shutil
import tempfile
import unittest
from testfixtures import TempDirectory


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
		shutil.rmtree(self.directory)

	@mock.patch('bench.submit.subprocess.check_output',
				return_value=fake_subprocess('sbatch script_10', True))
	def test_submit(self, _):
		index = 0
		pause = None
		reservation = None
		qos = None
		account = None
		new_index = bench.submit.submit(self.directory, self.folder,
							 			index, pause, reservation, qos, account)

		#Did it find the file?
		self.assertEqual(1,new_index)

		


if __name__ == '__main__':
	unittest.main()