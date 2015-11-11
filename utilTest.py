import unittest
from graphUtil import toCartesian

#Unit test for ensuring GPS coordinates are within range
class TestFunctions(unittest.TestCase):

	def test_toCartesian(self):
		testCoordinatesBAD = {
			1:'-33 43.243 -12 35.345'
			, 2: '-181 0.0 87 0.0'
		}

		testCoordinatesGOOD = {
			1: '-90 0.0 -180 0.0'
		}

		try:
			toCartesian(testCoordinatesGOOD)
		except:
			self.fail("This should not fail!!!")

		with self.assertRaises(ValueError):
			toCartesian(testCoordinatesBAD) 

if __name__ == '__main__':
	unittest.main()