import logging
import scrapy
from urllib.parse import urljoin, unquote
import pandas as pd
import numpy as np


class ZaeSpider(scrapy.Spider):
    name = "production_google_parse"

    def start_requests(self):
        #dataframe = pd.read_csv('data/drovoseki.csv')
        #urls = list(dataframe['Краткое наименование'])
        urls = [
            "https://www.heleos.ru/catalog_laminators/",
            "http://www.decon.ru"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.find_production, meta={'company_name': url})


    def find_production(self, response):
        arr =[]
        for item in response.css('li *'):
            arr.append("".join(item.re(r"[А-Я][ A-zА-яЁё0-9:]+")))

        yield {
            "items": [x for x in arr if len(x) > 0]
        }
        
