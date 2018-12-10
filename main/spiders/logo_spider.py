import logging
import scrapy
from urllib.parse import urljoin, unquote
import pandas as pd
import numpy as np


class ZaeSpider(scrapy.Spider):

    name = "logo"


    def start_requests(self):
        dataframe = pd.read_csv('data/drovoseki.csv')
        urls = list(dataframe['Краткое наименование'])
        for url in urls:
            search_url = 'https://yandex.ru/search/?lr=213&text=' + url + '%20-list-org%20-zachestnyibiznes%20-sbis'
            yield scrapy.Request(url=search_url, callback=self.find_links, meta={'company_name': url})


    def find_links(self, response):
        LINK_SELECTOR = '.link_theme_outer>b::text'
        for link in response.css(LINK_SELECTOR):
            #yield { "link": "http://www." + link.extract() }
            site = "http://www." + link.extract()
            yield scrapy.Request(site, self.parse_site, meta={'company_name': response.meta.get('company_name'), 'site': site})

    def parse_site(self, response):
        company_name = response.meta.get('company_name')
        keywords = company_name.replace("ООО", "").replace("\"", "").lower().split(' ')
        keywords = [x for x in keywords if len(x) > 3]
        META_SELECTOR = 'title::text, meta::attr(content)'

        flag = False
        for meta in response.css(META_SELECTOR):
            for keyword in keywords:
                if keyword in meta.extract().replace("\"", "").lower():
                    if len(meta.re("(дерев)|(древ)")) != 0:
                        flag = True

        if flag:
            img_list = response.css('img::attr(src)').extract()

            img_src = [x for x in img_list if 'logo' in x]
            if len(img_src) > 0:
                img_src = img_src[0].replace("//", "/")

                if img_src.startswith("http"):
                    yield {
                        'name': response.meta.get('company_name'),
                        'site': response.meta.get('site'),
                        'img_src': img_src
                    }
                else:
                    yield {
                        'name': response.meta.get('company_name'),
                        'site': response.meta.get('site'),
                        'img_src': response.meta.get('site') + img_src
                    }
