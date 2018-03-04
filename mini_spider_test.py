#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: mini_spider_test.py
Author: zhenglin(zhenglin@baidu.com)
Date: 2016/12/25 16:03:17
"""




import os
import sys

import unittest

import common_func
import my_crawler
import logTools
import parse_conf
import logging


log = logTools.Log(logging.DEBUG)


class MiniSpiderTestCase(unittest.TestCase):
    """
    @note:测试mini_spider
    """
    def setUp(self):
        self.mini_spider = my_crawler.MyCrawler('./conf/spider.conf')

    def tearDown(self):
        pass

    def testParseConf(self):
        """
        @测试解析配置文件
        """
        config = parse_conf.ParseConf("./conf/spider.conf")
        config.setConf()
        self.assertEqual("./output", config.outputPath)
        self.assertEqual(3, config.maxDepth)
        self.assertEqual(1, config.crawlInterval)
        self.assertEqual(5, config.crawlTimeout)
        self.assertEqual(8, config.threadCount)
       
    def test_crawlInterval(self):
        """
        @note:测试url解析
        """ 
        expectedUrl = 'http://pycm.baidu.com:8081/'
        self.mini_spider.urlFilePath = './conf/url'
        self.mini_spider.creatQueueByUrlList()
        self.assertEqual([expectedUrl, 0], self.mini_spider.uncrawlQueue.get())
  
    def testCheckPattern(self):
        """
        @note:测试匹配规则
        """ 
        self.assertTrue(self.mini_spider.checkAimPat('http://www.baidu.com:123.1.jpg'))
        self.assertTrue(self.mini_spider.checkAimPat('http://www.baidu.com:123.1.png'))
        self.assertTrue(self.mini_spider.checkAimPat('http://www.baidu.com:123.1.gif'))
        self.assertTrue(self.mini_spider.checkAimPat('http://www.baidu.com:123.1.bmp'))


              
 
if __name__ == '__main__':
    unittest.main()
