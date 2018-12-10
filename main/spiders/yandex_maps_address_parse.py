import scrapy
from urllib.parse import unquote
import json

lang = 'ru_RU'
org_type = 'biz'
results = '10'
apikey = 'acaa8f33-45d7-49eb-b57d-d96f7f3cd49c'
text = unquote("117639, г. Москва, проспект Балаклавский, д. 2 корп. 6 ком. 6")
url = 'https://search-maps.yandex.ru/v1/?lang='+lang+'&type='+org_type+'&results='+results+'&apikey='+apikey+'&text='+text
keywords = '' #'Производство пива'.split(' ')

class Yecom(scrapy.Spider):
    name = "yecom"

    def start_requests(self):
        url = 'http://yecom.ru/search/?query=7726376856'
        yield scrapy.Request(url=url, callback=self.find)

    def find(self, response):
        NEXT_PAGE_SELECTOR = '#companies>.company>a'
        for link in response.css(NEXT_PAGE_SELECTOR):
            yield response.follow(link, self.parse)

    def parse(self, response):
        KEYWORDS_SELECTOR = '#content-780>.company-title.mb10 + p'
        for found_keywords in response.css(KEYWORDS_SELECTOR):
            #yield { 'keywords': keywords.css('::text').extract_first() }
            keywords = found_keywords.split(' ')
            yield scrapy.Request(url=url, callback=self.process_map_data)

    def yandex_maps_request(self, response):
        yield scrapy.Request(url=url, callback=self.process_map_data)

    def process_map_data(self, response):
        data = json.loads(response.body)
        for item in data['features']:
            flag = False
            companyMeta = item['properties']['CompanyMetaData']
            for category in companyMeta['Categories']:
                for keyword in keywords:
                    if not flag:
                        if keyword.lower()[:len(keyword)] in category['name'].lower():
                            flag = True
            if 1:
                yield { "name": companyMeta['name'] }