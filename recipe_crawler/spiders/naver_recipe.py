#-*- coding: utf-8 -*-

import scrapy
import re
import json
import requests
from urlparse import urlparse, parse_qs
from HTMLParser import HTMLParser

visited = {}

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
class NaverRecipeSpider(scrapy.Spider):
    # 에이전트
    name = 'naver_recipe'
    # 씨앗 URL
    start_urls = ['http://terms.naver.com/list.nhn?cid=48156&categoryId=48156']

    # 맨 처음 실행되는 콜백
    def parse(self, response):
        # 카테고리 목록 추출
        categories = response.css('#content > div.loca_m > div > ul > li > a::attr(href)').extract()

        if (len(categories)):
            # 하위 카테고리가 있을 때
            # 하위 카테고리로 다시 들어간다
            for category in categories:
                # 카테고리 방문 기록 생성
                query = getQueries(category)
                visited[query['categoryId']] = {}

                yield scrapy.Request(response.urljoin(category), self.parse)
        else:
            # 하위 카테고리가 없을 때
            yield scrapy.Request(response.url + '&page=1', self.parsePage)

    # 모든 페이지를 열람하는 콜백
    def parsePage(self, response):

        # 페이징 목록을 가져온다
        # 다른 페이지도 파싱해야 함
        for page in response.xpath('//*[@id="paginate"]/a'):
            # 페이지 풀 URL 생성, 쿼리스트링 파싱
            url = response.urljoin(page.xpath('@href').extract()[0])
            query = getQueries(url)

            yield scrapy.Request(url, self.parsePage)

        # 모든 레시피를 파싱한다
        for recipe in response.css('#content > div.lst_wrap.sub > ul > li > dl > dt > a:nth-child(1)'):
            url = response.urljoin(recipe.xpath('@href').extract()[0])
            yield scrapy.Request(url, self.parseRecipe)


        # 요리과정 텍스트
        recipe['method'] = ''.join([strip_tags(x) for x in response.xpath((
            u"//h4[contains(text(), '요리과정')]"
            + nextRange +
            u"/preceding-sibling::p[preceding-sibling::h4[contains(text(), '요리과정')]]"
        )).extract()])

        recipe['method'] = re.split(r"\d{0,2}\.\s", recipe['method'])

        # 요리과정 이미지
        recipe['methodThumb'] = response.xpath((
            u"//h4[contains(text(), '요리과정')]"
            + nextRange +
            u"/preceding-sibling::div[preceding-sibling::h4[contains(text(), '요리과정')]]/a/img/@origin_src"
        )).extract()

        # 작은 이미지 주소로 변환
        if (recipe.get('methodThumb') != None):
            for index, thumbSrc in enumerate(recipe['methodThumb']):
                recipe['methodThumb'][index] = thumbSrc.replace("m4500_4500_fst_n", "w224_fst_n")

        # 원본 주소
        recipe['origin'] = response.url

        # 제목 변경
        recipe['title'] = recipe['title'].replace(u' 만드는 법', '')


        # 데이터를 줄이기 위해 불필요한 항목 삭제
        del recipe['basic']
        del recipe['food']

      


        yield recipe
