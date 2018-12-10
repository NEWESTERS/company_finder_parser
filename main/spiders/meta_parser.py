import logging
import scrapy
from urllib.parse import urljoin, unquote
import pandas as pd
import numpy as np


class MetaParser(scrapy.Spider):

    name = "meta_parser"

    def start_requests(self):
        urls = [ "http://standartwood.ru" ]
        for url in urls:
            search_url = url
            yield scrapy.Request(url=search_url, callback=self.parse)

    def parse(self, response):
        META_SELECTOR = 'title::text, meta::attr(content)'
        layer1, layer2 = False, False
        for meta in response.css(META_SELECTOR):

            if len(meta.re("(дерев)|(древ)")) != 0:
                layer1 = True
                
            if len(meta.re("(конструкц)|(издели)|(производств)")) != 0:
                layer2 = True

        yield { "checked": layer1 and layer2 }

