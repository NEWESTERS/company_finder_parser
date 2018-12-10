import scrapy
from urllib.parse import urljoin, unquote
import numpy

class MetaParser(scrapy.Spider):

    name = "meta_parser"

    def start_requests(self):
        urls = [ "http://вудворкер.рф" ]
        for url in urls:
            search_url = url
            yield scrapy.Request(url=search_url, callback=self.parse)

    def parse(self, response):
        phones = response.xpath('string(//body)').re(r"[78]?[- ]?[(]?[0-9]{3}[)]?[- ]?[0-9]{3}[- ]?[0-9]{2}[- ]?[0-9]{2}")
        emails = response.xpath('string(//body)').re(r"[A-z\dА-яЁё._-]+[@][A-z\dА-яЁё]+[.][A-zА-яЁё]+")
        #addresses = response.xpath('string(//body)').re("([\"]?[ А-яЁё]*[.]?[ ]?[А-яЁё\d]+[,]?[\"]?(\n)?((<br>)|(<br />))?(\n)?){1,}")
        about = "".join(response.css('p::text').re(r"[ А-яЁё\-.,\n«»]"))
        
        yield {
            "phones": numpy.unique(numpy.array(phones)),
            "emails": numpy.unique(numpy.array(emails)),
            #"addresses": numpy.unique(numpy.array(addresses))
            "about": about
        }

