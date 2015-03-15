# -*- coding: utf-8 -*-

import unittest

import rmqops


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.rmq = rmqops.RMQOps()

    def tearDown(self):
        pass



if __name__ == '__main__':
    unittest.main()
