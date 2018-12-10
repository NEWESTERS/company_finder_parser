import scrapy

class NalogIo(scrapy.Spider):
    name = "nalog_io"

    def start_requests(self):
        urls = [
            'https://nalog.io/inn/7708118919'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        SET_SELECTOR = '.company-information>table tr:nth_child(3)>td:nth_child(2)'
        for brickset in response.css(SET_SELECTOR):
            NAME_SELECTOR = 'b::text'
            yield {
                'status': brickset.css(NAME_SELECTOR).extract_first(),
            }