#-*- coding: utf-8 -*-

import scrapy
import re
import json
import requests
from urlparse import urlparse, parse_qs
from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

# 태그 제거
def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

# URL QueryString 파싱
def getQueries(url):
    query = parse_qs(urlparse(url).query)

    for attr, value in query.items():
        query[attr] = query[attr][0];

    return query

# 스파이더
class CategorySpider(scrapy.Spider):
    # 에이전트
    name = 'recipe_category'
    # 씨앗 URL
    start_urls = ['http://terms.naver.com/list.nhn?cid=48156&categoryId=48156']

    # 맨 처음 실행되는 콜백
    def parse(self, response):
        # 카테고리 목록 추출
        categories = response.xpath('//div[@id="content"]/div[@class="loca_m"]/div[@class="m_detail"]/ul/li/a')

        if (len(categories)):
            # 하위 카테고리가 있을 때
            # 하위 카테고리로 다시 들어간다
            for category in categories:
                url = response.urljoin(category.xpath('@href').extract()[0])
                query = getQueries(url)
                label = category.xpath('.//span/text()').extract()[0]

                item = {
                    'id': query['categoryId'],
                    'label': label,
                }

                yield item

                # requests.post("http://localhost:1337/category", data=item)

                yield scrapy.Request(url, self.parse)
