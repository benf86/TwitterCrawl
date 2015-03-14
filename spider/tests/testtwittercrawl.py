# -*- coding: utf-8 -*-

import unittest

import spider


class TestTwitterCrawl(unittest.TestCase):
    def setUp(self):
        self.spider = spider.Spider()
        with open('seed.txt', 'w') as f:
            f.write('benjiferreira\npu7r')

    def tearDown(self):
        pass

    def test_get_seed_user(self):
        self.assertEqual(['benjiferreira', 'pu7r'],
                         self.spider.get_seed_users())

    def test_crawl(self):
        self.spider.crawl()


if __name__ == '__main__':
    unittest.main()