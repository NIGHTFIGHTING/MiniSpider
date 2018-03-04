#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import threading

import chardet
import ConfigParser
import HTMLParser
import posixpath
import Queue
import re
import urlparse
import argparse
import requests

import common_func
import parse_conf
import logTools
import logging


log = logTools.Log(logging.DEBUG)

class MyCrawler(object):
    """
        MyCrawler包含以下函数:
        creatQueueByUrlList : 解析url,创建爬行队列
        crawlInterface : 爬行、创建和管理爬行线程的接口
        crawlExcute : 从队列中获取没有抓取的url，执行抓取
        checkAimPat : 检查URL匹配目标模式
        saveData : 保存抓取的数据
        checkUrl : 检查url是否已经抓取过
        updateCrawlSet : 更新已抓取和未抓取队列
        addUncrawlSet : 把新解析的url增加到未抓取队列
    """

    def __init__(self, confFilePath):
        """
        @note:定义和初始化类成员
        """
        self.FreeThreadNum = 0
        self.uncrawlQueue = Queue.Queue(maxsize=-1)
        self.crawledUrl = set()
        self.crawlingUrl = set()
        self.freeThread = threading.Lock()
        self.runningThreads = []
        
        # parse conf
        self.config = parse_conf.ParseConf(confFilePath)
        self.config.setConf()
    
    def __exit__(self):
        pass

    def creatQueueByUrlList(self):
        """
        @note:解析url和初始化爬行队列,如果创建队列成功，则返回true，否则返回false。
        """
        parentDepth = 0
        urlFp = None

        with open(self.config.urlFilePath) as urlFp:
            urlContent = urlFp.read()
            if len(urlContent) == 0:
                log.warning("urlFilePath: %s is empty" % self.config.urlFilePath)
                return False

            seedTemp = urlContent.split('\n')
            seedTemp.remove('')
            seedFromUrl = list(set(seedTemp))

            for seedUrl in seedFromUrl:
                self.uncrawlQueue.put([seedUrl, parentDepth])
                log.info("initial uncrawlQueue size:%d" % self.uncrawlQueue.qsize())
        return True

    def crawlInterface(self):
        """
        @note:爬行、创建和管理爬行线程的接口
        """
        log.info("mini_spider start")
       # print "mini_spider start"

        if not self.creatQueueByUrlList():
            return False

        for i in range(self.config.threadCount):
            t = threading.Thread(target=self.crawlExcute) 
            t.setDaemon(True)
            self.runningThreads.append(t)
            self.FreeThreadNum += 1
            log.info("current free thread number %d" % self.FreeThreadNum)
            t.start()
            time.sleep(self.config.crawlInterval)

        for i in self.runningThreads:
            t.join(self.config.crawlTimeout)

        log.info("mini_spider  finish")
        #print "mini_spider finish"
        return True

    def crawlExcute(self):
        """
        @note:从队列中获取任务执行抓取
        """
        isFree = True
        threadName = threading.currentThread().getName()

        while True:
            #如果空闲线程数等于线程总数，并且待爬虫队列为空
            with self.freeThread:
                runningThreadLen = len(self.runningThreads)
                if self.FreeThreadNum == runningThreadLen and self.uncrawlQueue.empty():
                    return 

            #检查可用的URL抓取任务和更新信息
            if self.uncrawlQueue.empty():
                log.info("[%s]no task, now free" % threadName)
                time.sleep(self.config.crawlInterval)
                continue

            if not isFree:
                time.sleep(self.config.crawlInterval)
                continue

            with self.freeThread:
                try:
                    newTask = self.uncrawlQueue.get(False)
                except Exception  as err:
                    log.info("[%s] get task failed" % err)
                    continue

                #开始抓取
                taskUrlFromQueue = newTask[0]
                taskUrlFromQueueDepth = newTask[1]
                log.info("[%s]get task: [url]:%s [depth]:%d"\
                         % (threadName, taskUrlFromQueue, taskUrlFromQueueDepth))

                if self.checkUrl(taskUrlFromQueue):
                    self.crawlingUrl.add(taskUrlFromQueue)
                    isFree = False
                    self.FreeThreadNum -= 1
                    log.info("[%s]change FreeThreadNum to %d" % (threadName, self.FreeThreadNum))
                    log.info("current uncrawled size:%d" % self.uncrawlQueue.qsize())
                    log.info("current crawling  size:%d" % len(self.crawlingUrl))
                    log.info("current crawled size:%d" % len(self.crawledUrl))
                else:
                    log.warning("[%s]task %s cancel" % (threadName, taskUrlFromQueue))

            if isFree:
                continue

            log.info("[%s]execute extend crawl queue" % threadName)
            self.addUncrawlSet(threadName, taskUrlFromQueue, taskUrlFromQueueDepth)
            log.info("[%s]add crawl queue finish" % threadName)

            #如果匹配目标模式，则调用存储URL数据接口
            if self.checkAimPat(taskUrlFromQueue):
                log.info("[%s] start to download" % threadName)
                self.saveData(threadName, taskUrlFromQueue)
                log.info("[%s]download success" % threadName)

            #更新爬行线程状态
            with self.freeThread:
                isFree = True
                self.FreeThreadNum += 1
                log.info("[%s]change FreeThreadNum to %d" % (threadName, self.FreeThreadNum))

            time.sleep(self.config.crawlInterval)

    def checkUrl(self, url):
        """
        @note:如果URL已被爬行或正在爬行，则返回false。否则返回true
        """
        if url in self.crawledUrl or url in self.crawlingUrl:
            return False
        else:
            return True

    def updateCrawlSet(self, threadName, targetUrl):
        """
        @note:添加targeturl到crawledurl删除crawlingurl
        """
        self.crawledUrl.add(targetUrl)
        if targetUrl in self.crawlingUrl:
            self.crawlingUrl.remove(targetUrl)
            log.info("[%s]remove %s from crawlingUrl" % (threadName, targetUrl))

        log.info("[%s] add %s to crawledUrl" % (threadName, targetUrl))
        log.info("current uncrawled size:%d" % self.uncrawlQueue.qsize())
        log.info("current crawling  size:%d" % len(self.crawlingUrl))
        log.info("current crawled size:%d" % len(self.crawledUrl))
    
    def addUncrawlSet(self, threadName, parentUrl, parentDepth):
        """
        @note:从上一层url中获取url，增加到未爬虫队列
        """
        userRequest = None
        userRespones = None

        if parentDepth > self.config.maxDepth:
            log.info("[%s]%s 's depth %d is deeper than max crawl depth"\
                      % (threadName, parentUrl, parentDepth))
            self.updateCrawlSet(threadName, parentUrl)
            return
        
        try:
            userRespones = requests.get(parentUrl, timeout = self.config.crawlTimeout)
            content = userRespones.content
        except requests.exceptions.ConnectionError as err:
            log.warning("[%s]get data %s failed, %s" % (threadName, parentUrl, str(err)))
            self.updateCrawlSet(threadName, parentUrl)
            return
        except Exception as err:
            log.warning("[%s]get data %s failed, %s" % (threadName, parentUrl, str(err)))
            self.updateCrawlSet(threadName, parentUrl)
            return
        
        #解析网页数据
        try:
            charset = chardet.detect(content)['encoding']
            if charset is None:
                log.info("get %s encoding failed." % (charset))
                return

            content = content.decode(charset).encode('utf-8')
            pageParser = common_func.GetUrlsFromPage()
            pageParser.feed(content)
            for i in range(len(pageParser.href)):
                fullUrl = common_func.ensureAbsolutelyUrl(parentUrl, pageParser.href[i])
                if self.checkUrl(fullUrl):
                    self.uncrawlQueue.put([fullUrl, parentDepth + 1])
                    log.info("[%s]put %s into uncrawled" % (threadName, fullUrl))
            pageParser.close()
        except HTMLParser.HTMLParseError as err:
            log.warning("parse web page failed: %s " % err)
        finally:
            self.updateCrawlSet(threadName, parentUrl)

    def checkAimPat(self, url):
        """
        @note:检查URL匹配target_pattern，如果匹配返回匹配结果，或返回空
        """
        matchPattern = self.config.searchPattern.match(url)
        return matchPattern

    def saveData(self, threadName, targetUrl):
        """
        @note:在输出目录中存储数据
        """
        userRequest = None
        userResponse = None

        try:
            userRespones = requests.get(targetUrl, timeout = self.config.crawlTimeout)
            content = userRespones.content
        except requests.exceptions.ConnectionError as err:
            log.warning("[%s]download data from %s failed,warning %s"\
                         % (threadName, targetUrl, str(err)))
            return
        except  Exception as err:
            log.warning("[%s]download data from %s failed,warning %s"\
                         % (threadName, targetUrl, str(err)))
            return
        finally:
            if userResponse:
                userResponse.close()
        fileName = targetUrl.replace("/", "_").replace(":", "_")
        filePath = os.path.join(self.config.outputPath, fileName)
        with open(filePath, "w") as fw:
            fw.write(content)
        log.info("[%s]target %s saved in %s successfully"
                      % (threadName, str(targetUrl), fileName))
        self.crawledUrl.add(targetUrl)


