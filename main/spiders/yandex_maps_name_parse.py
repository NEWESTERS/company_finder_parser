import logging
import scrapy
from scrapy_splash import SplashRequest
from urllib.parse import unquote
import pandas as pd
import numpy as np

class YandexMapsNameParse(scrapy.Spider):
    name = "yandex_maps_name_parse"
    #url = "https://yandex.ru/maps/213/moscow/?text=" + unquote("ООО \"СИП \"БИЛДИНГ\"")

    def start_requests(self):
        dataframe = pd.read_csv('data/drovoseki.csv')
        names = list(dataframe['Краткое наименование'])
        for name in names:
            url = "https://yandex.ru/maps/213/moscow/?text=" + unquote(name)
            yield SplashRequest(url, self.parse, args={ 'wait': 2 }, meta={ 'company_name': name })

    def parse(self, response):
        BUSINESS_CARD_SELECTOR = '.business-card-view'
        yield {"some": response.css(BUSINESS_CARD_SELECTOR).extract_first()}
        if response.css(BUSINESS_CARD_SELECTOR) == None:
            URL_SELECTOR = '.business-urls-view__url::attr(href)'
            url = response.css(URL_SELECTOR).extract_first()

            ADDRESS_SELECTOR = '.business-card-view__address::text'
            address = response.css(ADDRESS_SELECTOR).extract_first()

            REMOVED_SELECTOR = '.business-status-warning-view__text::text'
            isWorking = True if response.css(REMOVED_SELECTOR) == None else False

            if url != None:
                yield scrapy.Request(url, self.parse_site, meta={
                    "site": url,
                    "address": address,
                    "isWorking": isWorking,
                    "company_name": response.meta.get('company_name')
                })
            else:
                yield {
                    "address": address,
                    "isWorking": isWorking
                }    

    def parse_site(self, response):
        company_name = response.meta.get('company_name')
        keywords = company_name.replace("ООО", "").replace("\"", "").lower().split(' ')
        keywords = [x for x in keywords if len(x) > 3]
        META_SELECTOR = 'title::text, meta::attr(content)'

        flag = False
        for meta in response.css(META_SELECTOR):
            for keyword in keywords:
                if keyword in meta.extract().replace("\"", "").lower():
                    #if len(meta.re("(дерев)|(древ)")) != 0:
                    flag = True

        if flag:

            # Production
            production = response.xpath("//*[text()[contains(., 'Продукция') or contains(., 'продукция')]]/@href").extract_first()
            catalog = response.xpath("//*[text()[contains(.,'Каталог') or contains(.,'каталог')]]/@href").extract_first()
            proizvodstvo = response.xpath("//*[text()[contains(.,'Производство') or contains(.,'производство')]]/@href").extract_first()
            tovary = response.xpath("//*[text()[contains(.,'Товары') or contains(.,'товары')]]/@href").extract_first()
            phones = response.xpath('string(//body)').re(r"[78]?[- ]?[(]?[0-9]{3}[)]?[- ]?[0-9]{3}[- ]?[0-9]{2}[- ]?[0-9]{2}")
            emails = response.xpath('string(//body)').re(r"[A-z\dА-яЁё._-]+[@][A-z\dА-яЁё]+[.][A-z]+")
            about = "".join(response.css('p::text').re(r"[ А-яЁё\-.,\n«»]"))

            production_hrefs = [x for x in [production, catalog, proizvodstvo, tovary] if x is not None]
            

            if len(production_hrefs) is not 0:

                for href in production_hrefs:
                    if href.startswith("http"):
                        logging.warning("outer HTTP")
                        logging.warning(href)
                        logging.warning(response.meta.get('company_name'))
                        logging.warning(response.meta.get('site'))

                        production_url = href

                    else:
                        logging.warning("outer NO HTTP")
                        logging.warning(response.meta.get('site') + href)
                        logging.warning(response.meta.get('company_name'))
                        logging.warning(response.meta.get('site'))

                        production_url = response.meta.get('site') + href
                    logging.warning('BEFORE VISITS')
                    logging.warning(response.meta.get('site'))
                    logging.warning(production_url)

                    visits_url = 'https://top100.rambler.ru/search?query=' + unquote(response.meta.get('site')) + '&range=month'
                    yield scrapy.Request(visits_url, self.parse_visits, meta={
                        'company_name': response.meta.get('company_name'),
                        'url': response.meta.get('site'),
                        'production_url': production_url,
                        'phones': phones,
                        'emails': emails,
                        'about': about,
                        'address': response.meta.get('address'),
                        'isWorking': response.meta.get('isWorking')
                    })
            else: 

                logging.warning('BEFORE VISITS WITHOUT LINKS')
                visits_url = 'https://top100.rambler.ru/search?query=' + unquote(response.meta.get('site')) + '&range=month'
                yield scrapy.Request(visits_url, self.parse_visits, meta={
                    'company_name': response.meta.get('company_name'),
                    'url': response.meta.get('site'),
                    'production_url': response.meta.get('site'),
                    'phones': phones,
                    'emails': emails,
                    'about': about,
                    'address': response.meta.get('address'),
                    'isWorking': response.meta.get('isWorking')
                })

    def parse_visits(self, response):
        STATISTICS_ROW_SELECTOR = '.projects-table__row'
        STATISTICS_CELL_SELECTOR = '.projects-table__cell'

        visits = None
        views = None

        for row in response.css(STATISTICS_ROW_SELECTOR):
            logging.warning("parsing " + response.meta.get('production_url') + " visits")
            visits = row.css(STATISTICS_CELL_SELECTOR + ':nth_child(2)>span::text').extract_first()
            views = row.css(STATISTICS_CELL_SELECTOR + ':nth_child(3)>span::text').extract_first()
       
        yield scrapy.Request(response.meta.get('production_url'), self.parse_production_links, meta={
            "company_name": response.meta.get('company_name'),
            "url": response.meta.get("url"),
            "visits": visits,
            "views": views,
            "phones": response.meta.get('phones'),
            "emails": response.meta.get('emails'),
            "about": response.meta.get('about'),
            'address': response.meta.get('address'),
            'isWorking': response.meta.get('isWorking')
        })

    def parse_production_links(self, response):
        logging.warning("I'M IN IMG FUNCTION")
        img_list = response.css('img::attr(src)').extract()

        production = {
            'logos': [],
            'products': []
        }

        for img_src in img_list:
            #img = img_src.replace("//", "/")
            logging.warning("img img img")
            flag = True

            if 'logo' in img_src:
                if img_src.startswith("http"):
                    production['logos'].append(img_src)

                else:
                    production['logos'].append(response.meta.get('url') + img_src)

            for word in ['yandex', 'thumb', 'background', 'banner', 'mail', 'rambler', 'themes', 'logo', 'counter']:
                if word in img_src:
                    flag = False

            if flag:
                if img_src.startswith("http"):
                    logging.warning("oops http")
                    production['products'].append(img_src)                    

                else:
                    logging.warning("no http lol")
                    production['products'].append(response.meta.get('url') + img_src)

        yield {
            'name': response.meta.get('company_name'),
            'url': response.meta.get('url'),
            'visits': response.meta.get('visits'),
            'views': response.meta.get('views'),
            'logos': np.unique(np.array(production['logos'])),
            'product_images': np.unique(np.array(production['products'])),
            "phones": response.meta.get('phones'),
            "emails": response.meta.get('emails'),
            "about": response.meta.get('about'),
            'address': response.meta.get('address'),
            'isWorking': response.meta.get('isWorking')
        }