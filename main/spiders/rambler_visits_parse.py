import scrapy
from urllib.parse import unquote

class RamberVisitsParse(scrapy.Spider):
    name = "rambler_visits_parse"
    url = 'www.primavera.ru'

    def start_requests(self):
        url = 'https://top100.rambler.ru/search?query=' + unquote(self.url) + '&range=month'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        STATISTICS_ROW_SELECTOR = '.projects-table__row'
        for row in response.css(STATISTICS_ROW_SELECTOR):
            STATISTICS_CELL_SELECTOR = '.projects-table__cell'
            yield {
                "visitors": row.css(STATISTICS_CELL_SELECTOR + ':nth_child(2)>span::text').extract_first(),
                "views": row.css(STATISTICS_CELL_SELECTOR + ':nth_child(3)>span::text').extract_first()
            }