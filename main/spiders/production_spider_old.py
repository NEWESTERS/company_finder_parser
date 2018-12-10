import logging
import scrapy
from urllib.parse import urljoin, unquote
import pandas as pd
import numpy as np


class ZaeSpider(scrapy.Spider):
    name = "production_google_parse_old"

    def start_requests(self):
        #dataframe = pd.read_csv('data/drovoseki.csv')
        #names = list(dataframe['Краткое наименование'])
        names = [
            'ООО "СИП \"БИЛДИНГ\"',
            'ООО \"ТАЙМЛОГИСТИК\"'
        ]
        for name in names:
            url = 'https://yandex.ru/search/?lr=213&text=' + name + '%20-list-org%20-zachestnyibiznes%20-sbis'
            yield scrapy.Request(url=url, callback=self.find_links, meta={ 'company_name': name })

    def find_links(self, response):
        LINK_SELECTOR = '.link_theme_outer>b::text'
        for link in response.css(LINK_SELECTOR):
            url = "http://www." + link.extract()
            yield scrapy.Request(url, self.parse_production, meta={
                'company_name': response.meta.get('company_name'),
                'url': url
            })

    def parse_production(self, response):
        logging.warning(response.meta.get('company_name'))
        company_name = response.meta.get('company_name')
        keywords = company_name.replace("ООО", "").replace("\"", "").lower().split(' ')
        keywords = [x for x in keywords if len(x) > 3]
        META_SELECTOR = 'title::text, meta::attr(content)'

        flag = False
        for meta in response.css(META_SELECTOR):
            for keyword in keywords:
                if keyword in meta.extract().replace("\"", "").lower():
                    if len(response.xpath("string(//body)").re(r"(дерев)|(древ)")) != 0:
                        flag = True

        if flag:
            production = response.xpath("//*[text()[contains(., 'Продукция')]]").extract_first()
            catalog = response.xpath("//*[text()[contains(.,'Каталог')]]").extract_first()
            proizvodstvo = response.xpath("//*[text()[contains(.,'Производство')]]").extract_first()
            tovary = response.xpath("//*[text()[contains(.,'Товары')]]").extract_first()
            phones = response.xpath('string(//body)').re(r"[78]?[- ]?[(]?[0-9]{3}[)]?[- ]?[0-9]{3}[- ]?[0-9]{2}[- ]?[0-9]{2}")
            emails = response.xpath('string(//body)').re(r"[A-z\dА-яЁё._-]+[@][A-z\dА-яЁё]+[.][A-z]+")
            about = "".join(response.css('p::text').re(r"[ А-яЁё\-.,\n«»]"))

            url = 'https://top100.rambler.ru/search?query=' + unquote(response.meta.get('url')) + '&range=month'
            yield scrapy.Request(url, self.parse_visits, meta={
                'views': response.meta.get('views'),
                'visitors': response.meta.get('visitors'),
                'name': company_name,
                'url': response.meta.get('url'),
                'production': production,
                'catalog': catalog,
                'proizvodstvo': proizvodstvo,
                'tovary': tovary,
                "phones": np.unique(np.array(phones)),
                "emails": np.unique(np.array(emails)),
                "about": about
            })

    def parse_visits(self, response):
        url = response.meta.get("url")
        STATISTICS_ROW_SELECTOR = '.projects-table__row'
        for row in response.css(STATISTICS_ROW_SELECTOR):
            STATISTICS_CELL_SELECTOR = '.projects-table__cell'
            yield {
                "name": response.meta.get('name'),
                "url": url,
                "visitors": row.css(STATISTICS_CELL_SELECTOR + ':nth_child(2)>span::text').extract_first(),
                "views": row.css(STATISTICS_CELL_SELECTOR + ':nth_child(3)>span::text').extract_first(),
                'production': response.meta.get('production'),
                'catalog': response.meta.get('catalog'),
                'proizvodstvo': response.meta.get('proizvodstvo'),
                'tovary': response.meta.get('tovary'),
                "phones": response.meta.get('phones'),
                "emails": response.meta.get('emails'),
                "about": response.meta.get('about')
            }
