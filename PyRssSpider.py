# -*- coding: UTF-8 -*-
import urllib2
import PyRSS2Gen
import re, random, datetime, sys, os, ssl, platform, sqlite3
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')

my_headers = [
    "Mozilla/5.0 (MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; WOW64; Trident/4.0; SLCC1)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; WOW64; Trident/4.0; SLCC1)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; WOW64; Trident/4.0; SLCC1)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en; rv:1.9.1.7) Gecko/20091221 Firefox/3.5.7",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20120427 Firefox/15.0a1",
    "Opera/9.80 (Macintosh; Intel Mac OS X; U; en) Presto/2.2.15 Version/10.00",
    "ozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
]


def get_host(url):
    '''
    通过url获取域名
    :param url: 带获取的url地址
    :return: host结果
    '''
    proto, rest = urllib2.splittype(url)
    res, rest = urllib2.splithost(rest)
    if res:
        return res
    else:
        print "获取host" + url + "失败"
        sys.exit(0)


def get_html(url, host='', min=False):
    '''
    获取网页源代码函数
    :param url: 待获取的url地址
    :param min: 是否压缩源代码
    :return:
    '''
    if host == '': host = get_host(url)
    if (url[0:5] == 'https') and (platform.system() == 'Windows'): ssl._create_default_https_context = ssl._create_unverified_context
    random_header = random.choice(my_headers)
    request = urllib2.Request(url)
    request.add_header("User-Agent", random_header)
    request.add_header("Host", host)
    request.add_header("Referer", "http://baidu.com/")
    request.add_header("GET", url)
    content = urllib2.urlopen(request).read()
    if min: content = re.sub(r'>\s+<', '><', content.replace('\t', '').replace('\r\n', '').replace('\n', '').replace('\r', ''))
    return content


def split(str, beg, end, reg=False):
    '''
    文本分割函数
    :param str: 待处理字符串
    :param beg: 分割开始位置
    :param end: 分割结束位置
    :param reg: 是否采用正则表达式
    :return: 处理结果
    '''
    if reg:
        if re.search(beg, str) and re.search(end, str):
            str = re.sub(r'([\s\S]*)' + beg, '', str)
            str = re.sub(end + r'([\s\S]*)', '', str)
            return str
        return -1;
    tmp1 = str.split(beg)
    if len(tmp1) >= 2:
        tmp2 = tmp1[1].split(end)
        if len(tmp2) >= 1: return tmp2[0]
        return -1
    return -1


def replace(old, new, string, reg=False, flags=0):
    '''
    字符串替换函数
    :param old: 源关键字
    :param new: 目标关键字
    :param string: 源字符串
    :param reg: 是否使用正则表达式
    :param flags: 正则表达式修饰符
    :return: 替换结果
    '''
    if reg:
        if re.search(old, string, flags=flags): return re.sub(old, new, string, flags=flags)
        return string
    else:
        return string.replace(old, new)


class RssSpider():
    def __init__(self, myrss, xmlpath, db, charset='utf-8'):
        self.url = myrss.link
        self.host = get_host(self.url)
        self.myrss = myrss
        self.xmlpath = xmlpath
        self.lists = []
        self.contents = []
        self.charset = charset
        # if os.path.isfile(self.xmlpath): os.remove(self.xmlpath)
        if os.path.isfile(db): conn = sqlite3.connect(db)
        else:
            conn = sqlite3.connect(db)
            conn.execute('''CREATE TABLE channel(id INT PRIMARY KEY     NOT NULL,
                                                 title          TEXT    NOT NULL,
                                                 link           TEXT    NOT NULL,
                                                 description    TEXT    NOT NULL,
                                                 atom_link      TEXT    NOT NULL);''')
            conn.execute('''CREATE TABLE item(id INT PRIMARY KEY     NOT NULL,
                                              title          TEXT    NOT NULL,
                                              link           TEXT    NOT NULL,
                                              description    TEXT    NOT NULL,
                                              comments       TEXT    NOT NULL,
                                              guid           TEXT    NOT NULL,
                                              pubDate        TEXT    NOT NULL);''')
            print  myrss.title, myrss.link, myrss.description
            # conn.execute("INSERT INTO channel (id,title,link,description,atom_link) \
            #               VALUES ('%d', '%s', '%s', '%s', '%s')" % \
            #                      (1, myrss.title, myrss.link, myrss.description, myrss.atom_link))
            # conn.commit()

    def save_rss_file(self):
        finallxml = self.myrss.to_xml(encoding='utf-8')
        file = open(self.xmlpath, 'w')
        file.writelines(finallxml)
        file.close()

    def _relative2absolute(self, url):
        if url[0:4] == 'http':
            return url
        elif url[0:5] == 'https':
            return url
        else:
            if self.url[0:5] == 'https':
                return 'https://' + self.host + '/' + url
            else:
                return 'http://' + self.host + '/' + url

    def get_list(self, reg, replaces=[], flag=0, min=False):
        '''
        获取文章列表
        :param reg: 正则表达式
        :param min: 是否压缩源码
        :return: 文章列表
        '''
        pageCode = get_html(self.url, min=False)
        if self.charset <> 'utf-8': pageCode.decode(self.charset).encode('utf-8')
        for repl in replaces: pageCode = replace(repl['old'], repl['new'], pageCode, repl['reg'], repl['flags'])
        pattern = re.compile(reg, flag)
        self.lists = re.findall(pattern, pageCode)
        return self.lists

    def get_content(self, beg, end, reg=False):
        '''
        获取文章正文
        :param beg:正文开始
        :param end:正文结束
        :param reg:是否采用正则表达式
        :return: 文章正文列表
        '''
        i = len(self.lists)
        if beg == '' and end == '':
            for item in self.lists[::-1]:
                print self._relative2absolute(item[0]) + '\n', item[1].decode(self.charset) + '\n'
                rss = PyRSS2Gen.RSSItem(
                    title=item[1].decode(self.charset),
                    link=self._relative2absolute(item[0]),
                    comments=self._relative2absolute(item[0]),
                    pubDate=datetime.datetime.now(),
                    description=item[1].decode(self.charset),
                    guid=self._relative2absolute(item[0]) + str(i)
                )
                self.myrss.items.append(rss)
                i = i - 1
        else:
            for item in self.lists[::-1]:
                if (platform.system() == 'Windows'):
                    print item[0] + '\n', item[1].decode(self.charset) + '\n'
                else:
                    print item[0] + '\n', item[1] + '\n'
                pageCode = get_html(item[0], min=False)
                if pageCode <> -1:
                    content = split(pageCode, beg, end, reg)
                    if content <> -1:
                        rss = PyRSS2Gen.RSSItem(
                            title=item[1],
                            link=item[0],
                            comments=item[0] + "#comments",
                            pubDate=datetime.datetime.now(),
                            description=beg + content + end,
                            guid=item[0] + str(i)
                        )
                        self.myrss.items.append(rss)
                        i = i - 1
                    else:
                        print "获取内容失败 ", item[0]
                        sys.exit(0)
                else:
                    print "获取内容失败 ", item[0]
                    sys.exit(0)
        self.myrss.items = self.myrss.items[::-1] # 将列表倒序排列
        return self.myrss.items
