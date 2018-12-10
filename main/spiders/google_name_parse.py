import scrapy
from urllib.parse import unquote

class GoogleNameParse(scrapy.Spider):
    name = "google_name_parse"
    search = "ООО \"СИП \"БИЛДИНГ\""

    def start_requests(self):
        url = 'https://yandex.ru/search/?lr=213&text=' + unquote(self.search) + '%20-list-org%20-zachestnyibiznes%20-sbis'
        yield scrapy.Request(url=url, callback=self.find_links)

    def find_links(self, response):
        LINK_SELECTOR = '.link_theme_outer>b::text'
        for link in response.css(LINK_SELECTOR):
            yield response.follow("http://www." + link.extract(), self.parse)

    def parse(self, response):
        keywords = self.search.replace("ООО", "").replace("\"","").lower().split(' ')
        keywords = [x for x in keywords if len(x) > 3]

        flag = False

        META_SELECTOR = 'title::text, meta::attr(content)'
        for meta in response.css(META_SELECTOR):
            for keyword in keywords:
                if keyword in meta.extract().replace("„", "").replace("“", "").replace("\"","").replace("«", "").replace("»", "").lower():
                    flag = True

        if flag:
            phones = response.xpath('string(//body)').re("[7,8]?[-, ]?[(]?[0-9]{3}[)]?[-, ]?[0-9]{3}[-, ]?[0-9]{2}[-, ]?[0-9]{2}")
            yield {
                "phone": phones,
                "url": response.request.url
            }