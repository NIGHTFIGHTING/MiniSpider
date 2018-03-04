#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logTools

import re
import ConfigParser
import os
import logging


log = logTools.Log(logging.DEBUG)

class ParseConf(object):
    """ 
    解析配置文件
    """

    def  __init__(self, confPath):
        """ 
        @note:初始化class
        """
        self.urlFilePath = None  
        self.outputPath = None  
        self.maxDepth = 0  
        self.crawlInterval = 0  
        self.crawlTimeout = 8  
        self.targetUrl = None  
        self.threadCount = 8  
        self.spiderVersion = "0" 
        self.confPath = confPath
        self.searchPattern = ""
            
    def setConf(self):
        """
        读取配置文件 
        """
        try:
            self.configureParse = ConfigParser.ConfigParser()
            self.configureParse.read(self.confPath)
            
            spiderSection = 'spider'
            self.urlFilePath = self.configureParse.get(spiderSection, 'url_list_file')
            
            self.outputPath = self.configureParse.get(spiderSection, 'output_directory')
            if not os.path.isdir(self.outputPath):
                os.makedirs(self.outputPath)
            else:
                clearFileCmd = ''.join(['rm -rf ', self.outputPath, '/*'])
                os.system(clearFileCmd)

            #set crawl process value
            self.maxDepth = self.configureParse.getint(spiderSection, 'max_depth')
            self.crawlInterval = self.configureParse.getint(spiderSection, 'crawl_interval')
            self.crawlTimeout = self.configureParse.getint(spiderSection, 'crawl_timeout')
            self.threadCount = self.configureParse.getint(spiderSection, 'thread_count')
            targetUrl = self.configureParse.get(spiderSection, 'target_url')
            self.searchPattern = re.compile(targetUrl)
        except ConfigParser.Error as err:
            log.warning("parse spider_conf failed. error: %s" % str(err))
            return False

        return True


if __name__ == '__main__':
    cp = ParseConf("./conf/spider.conf")
    cp.setConf()
    #print cp.crawlTimeout
