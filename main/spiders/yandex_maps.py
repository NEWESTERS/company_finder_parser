import scrapy
from urllib.parse import unquote
import json

lang = 'ru_RU'
org_type = 'biz'
results = '10'
apikey = 'acaa8f33-45d7-49eb-b57d-d96f7f3cd49c'
text = unquote("117639, г. Москва, проспект Балаклавский, д. 2 корп. 6 ком. 6")
url = 'https://search-maps.yandex.ru/v1/?lang='+lang+'&type='+org_type+'&results='+results+'&apikey='+apikey+'&text='+text
keywords = 'Производство пива'.split(' ')


def yandex_maps_request():
    yield scrapy.Request(url=url, callback=process_map_data)

def process_map_data(response):
    data = json.loads(response)
    for item in data['features']:
        flag = False
        companyMeta = item['properties']['CompanyMetaData']
        for category in companyMeta['Categories']:
            for keyword in keywords:
                if not flag:
                    if keyword.lower()[:len(keyword)] in category['name'].lower():
                        flag = True
        if 1:
            yield companyMeta['name']

print(yandex_maps_request())