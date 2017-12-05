#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# __author__ = 'njuzwr'
from urllib import request
from urllib import error
import re


class QSBK:
    def __init__(self):
        self.index = 1
        self.header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                                     " AppleWebKit/537.36 (KHTML, like Gecko) "
                                     "Chrome/58.0.3029.96 Safari/537.36"}
        self.url = 'https://qiushibaike.com/hot/page/'
        self.domain = "https://www.qiushibaike.com"
        self.enable = False
        self.stories = []

    def get_page(self, index=None, content_url=None):
        try:
            response = None
            if index:
                req = request.Request(self.url+str(index), headers=self.header)
                response = request.urlopen(req)
            elif content_url:
                req = request.Request(self.domain + content_url, headers=self.header)
                response = request.urlopen(req)
            return response.read().decode('utf-8')  # decode format
        except error.URLError as e:
            print('Fail to get page' + str(index))
            if hasattr(e, "code"):
                print(e.code)
            if hasattr(e, "reason"):
                print(e.reason)
            return None

    def get_page_items(self, index):
        content = self.get_page(index)

        pattern = re.compile('''<div class="article block untagged mb15.*?<h2>(.*?)</h2>'''
                             + '''.*?<a href="(.*?)"'''
                             + '''.*?<span>(.*?)</span>'''
                             + '''.*?<!-- 图片或gif -->(.*?)<div class="stats">'''
                             + '''.*?<span class="stats-vote"><i class="number">(.*?)</i>''', re.S)
        items = re.finditer(pattern, content)
        # 这个地方如果使用findall是有问题的,匹配的是五个分组，而无法得到整个match对象
        # 注意findall 和 finditer的区别
        page_items = []
        for item in items:
            if "img" not in item[3]:
                if not re.search('查看全文', item.group()):
                    result = re.sub('<br/>', '\n', item.group(3))
                    page_items.append([item.group(1).strip(), result.strip(), item.group(5).strip()])
                else:
                    content_full = self.get_page(content_url=item.group(2))
                    pattern_full = re.compile('''<div class="article.*?<h2>(.*?)</h2>'''
                                              + '''.*?<div class="content">(.*?)</div>'''
                                              + '''.*?<span class="stats-vote"><i class="number">(.*?)</i>''', re.S)
                    item_full = re.findall(pattern_full, content_full)
                    print(item_full)
                    # item_full是一个list， 元素也是list
                    result = re.sub('<br/>', '\n', item_full[0][1])
                    page_items.append([item_full[0][0].strip(), result.strip(), item_full[0][2].strip()])

        return page_items

    def load_page(self):
        if self.enable:
            if len(self.stories) < 2:
                page_stories = self.get_page_items(self.index)
                if page_stories:
                    self.stories.append(page_stories)
                    self.index += 1

    def get_one_story(self, page_stories, page):
        for story in page_stories:
            recive = input()
            self.load_page()
            if recive == 'Q' or recive == 'q':
                self.enable = False
                return
            print('current page:%s\n publisher:%s\n content:%s\n vote:%s\n' % (page, story[0], story[1], story[2]))

    def start(self):
        self.enable = True
        self.load_page()
        current_page = 0
        while self.enable:
            if len(self.stories) > 0:
                page_stories = self.stories[0]
                current_page += 1
                del self.stories[0]
                self.get_one_story(page_stories, current_page)


if __name__ == "__main__":
    spider = QSBK()
    spider.start()

