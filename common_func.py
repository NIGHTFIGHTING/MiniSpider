#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import getopt
import HTMLParser
import logging
import urlparse
import posixpath

import logTools

log = logTools.Log(logging.DEBUG)

def ensureAbsolutelyUrl(parentUrl, hrefAttribute):
    """ 
    @note:确保链接是一个绝对的Url
    """
    if not hrefAttribute.startswith('http'):
        hrefAttribute = urlparse.urljoin(parentUrl, hrefAttribute)
        parsedTuple = urlparse.urlparse(hrefAttribute)
        normalPath = posixpath.normpath(parsedTuple[2])
        hrefAttribute = urlparse.urlunparse((parsedTuple.scheme,
                                    parsedTuple.netloc,
                                    normalPath, 
                                    parsedTuple.params,
                                    parsedTuple.query, 
                                    parsedTuple.fragment))
    return hrefAttribute


class GetUrlsFromPage(HTMLParser.HTMLParser):
    """
    @note:解析网页数据并返回提取的URL列表
    """
    def __init__(self):
        self.href = []
        HTMLParser.HTMLParser.__init__(self)

    def handle_starttag(self, webTags, hrefAttribute):
        if webTags == 'a':
            for (name, value) in hrefAttribute:
                if name == 'href':
                    if 0 <= value.replace(' ', '').find('javascript:location.href='):
                        valueTemp = value.replace('javascript:location.href=', '')
                        value = valueTemp.replace('"', '')
                    self.href.append(value)
        elif webTags == 'img':
            for (name, value) in hrefAttribute:
                if name == 'src':
                    self.href.append(value)
    

