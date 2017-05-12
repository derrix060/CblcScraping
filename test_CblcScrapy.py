import unittest
import requests
import CblcScrapy


class CblcTestCase(unittest.TestCase):
    def testEmpRegConnection(self):
        req = requests.get(CblcScrapy.Downloaders.EMPRESTIMOS_REGISTRADOS_URL)
        self.assertEqual(req.status_code, 200)


class CblcTestSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, map(CblcTestCase,
                                              ("testEmpRegConnection")))


if __name__ == '__main__':
    unittest.main()