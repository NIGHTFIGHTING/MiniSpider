#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging


import parse_conf
import my_crawler
import argparse
import logTools


log = logTools.Log(logging.DEBUG)

def main():
    """
    @note:爬虫入口函数
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help = "show the version", default = 0, action = "count")
    parser.add_argument("-c", "--config", help = "set config")
    args = parser.parse_args()

    if args.verbose == 1:
        print "version 1.0"
        return 0
    if args.config is not None:
        config = args.config

    spider = my_crawler.MyCrawler(config)
    
    if not spider.crawlInterface():
        log.info("spider run failed")
        return 1
    log.info("spider run succeed")
    return 0
    
if __name__ == '__main__':
    sys.exit(main())
