# Recipe-Crawler

## Introduction

Scrapy를 이용하여 '네이버 요리백과'를 크롤링 하는 엔진입니다.

## Installation
```
pip install Scrapy
```

## How to run

```
scrapy crawl recipe_category -o categories.json // 레시피 카테고리 목록
scrapy crawl naver_recipe -o recipes.json // 레시피 정보
```
