__author__ = 'ZhenHappy'
# -*- coding:utf-8 -*-
import urllib2
import re
import chardet #字符集检测

url = 'http://www.elm-world.com/newpage11.html'
headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
try:
    request = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(request)
    content = response.read().decode('CP932').encode('utf-8')
    # result = chardet.detect(content)
    # encoding = result['encoding']
    # print encoding
    # print content
    content.replace('<img src="extremesex/memder/ng/logo31.gif" width="47" height="25" border="0" alt="New!">','')
    pattern = re.compile(r'<a href="(.*?)" target="_blank">(.*?)</a><br>',re.S)
    items = re.findall(pattern, content)
    # print len(items)
    # print items
    for item in items:
        # print len(item)
        print item[0]+'\n',item[1]+'\n'

except urllib2.URLError, e:
    if hasattr(e, "code"):
        print e.code
    if hasattr(e, "reason"):
        print e.reason
