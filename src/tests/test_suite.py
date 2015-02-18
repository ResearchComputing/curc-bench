#Automated test suite for curc-bench
import unittest

#Trying to get automated tests to run
def unimportant_test():
	return 1

class MyTest(unittest.TestCase):
    def test(self):
        self.assertEqual(unimportant_test(), 1)


# unimportant_test()