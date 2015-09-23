# -*- coding: UTF-8 -*-
import re
import PyRSS2Gen
from PyRssSpider import RssSpider
import datetime

myrss = PyRSS2Gen.RSS2(
    title='八社福利站',
    link='http://www.8she.com/',
    atom_link='http://117.28.237.21:29956/ording/resource/8she.xml',
    description='八社福利站',
    lastBuildDate=datetime.datetime.now(),
    language="zh-CN",
    items=[]
)

def main():
    rssSpider = RssSpider(myrss, '8She.xml', '8She.db')
    rssSpider.get_list(r'<header>.*?<i></i></a><h2><a href="(.*?)" title=".*?">(.*?)</a></h2></header>', flag=re.S)
    rssSpider.get_content('<article class="article-content">', '</article>')
    rssSpider.save_rss_file()

if __name__ == '__main__':
    main()
