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

class TestSubmit (unittest.TestCase):

	@mock.patch('bench.submit.subprocess.check_output',
				return_value=fake_subprocess('sbatch script_10', True))
	def test_submit(self):
		d = TempDirectory()
		path = d.write(('folder', 'script_10'), b'text in the script')
		index = 0
		pause = None
		reservation = None
		bench.submit.submit(d, d.folder, index, pause, reservation)
		self.assertEqual(1,1)
