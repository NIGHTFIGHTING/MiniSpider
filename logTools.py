#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os


class Log(object):
    """
    @note:调试日志工具类
    """
    def __init__(self, logLevel):
        """
        initial class
        """
        self.log_level = logLevel
        self.log_format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
        self.log_date_fmt = '%Y-%m-%d %H:%M:%S'
        
        logFile = "./log/mini_spider.log"
        if not os.path.exists(logFile):
            os.system("mkdir log")
            os.system("touch %s" % logFile)
        self.log_filename = logFile
        
        self.log_filemode = 'w'  # 默认'a'
        self.memory_usage = '0.00M'
        
        """
        加载配置信息
        """
        logging.basicConfig(
            level=self.log_level,
            format=self.log_format,
            datefmt=self.log_date_fmt,
            filename=self.log_filename,
            filemode=self.log_filemode
        )

    def get_memory_usage(self):
        """
        @note:获取当前进程内存使用情况(单位M)
        """
        # 获取当前脚本的进程ID
        pid = os.getpid()
        # 获取当前脚本占用的内存
        cmd = 'ps -p %s -o rss=' % pid
        output = os.popen(cmd)
        result = output.read()
        if result == '':
            memory_usage_value = 0
        else:
            memory_usage_value = int(result.strip())
        memory_usage_format = memory_usage_value / 1024.0
        #print '内存使用%.2fM' % memory_usage_format
        self.memory_usage = '%.2fM' % memory_usage_format

    @staticmethod
    def debug(msg):
        """
        @note:装饰 debug 
        """
        logging.debug(msg)

    @staticmethod
    def info(msg):
        """
        @note:装饰 info
        """
        logging.info(msg)

    @staticmethod
    def warning(msg):
        """
        @note:装饰 warning
        """
        logging.warning(msg)


def test_log(logFevel):
    """
    @note:实例化，修改日志文件名称，加载新配置
    """
    xxx = Log(logFevel)
    #xxx.log_filename = 'miniSpider.log'
    #xxx.log_config()
    # 测试
    xxx.debug('This is debug message')
    xxx.info('This is info message')
    xxx.warning('This is warning message')


if __name__ == '__main__':
    test_log(logging.DEBUG)


'''
默认情况下，logging将日志打印到屏幕，日志级别为WARNING；
日志级别大小关系为：CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET
logging.basicConfig函数各参数:
filename: 指定日志文件名
filemode: 和file函数意义相同，指定日志文件的打开模式，'w'或'a'
format: 指定输出的格式和内容，format可以输出很多有用信息，如上例所示:
    %(levelno)s: 打印日志级别的数值
    %(levelname)s: 打印日志级别名称
    %(pathname)s: 打印当前执行程序的路径，其实就是sys.argv[0]
    %(filename)s: 打印当前执行程序名
    %(funcName)s: 打印日志的当前函数
    %(lineno)d: 打印日志的当前行号
    %(asctime)s: 打印日志的时间
    %(thread)d: 打印线程ID
    %(threadName)s: 打印线程名称
    %(process)d: 打印进程ID
    %(message)s: 打印日志信息
datefmt: 指定时间格式，同time.strftime()
level: 设置日志级别，默认为logging.WARNING
stream: 指定将日志的输出流，可以指定输出到sys.stderr,sys.stdout或者文件，默认输出到sys.stderr，当stream和filename同时指定时，stream被忽略
'''
