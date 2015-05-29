# -*- coding: utf-8 -*-

import scrapy
import urlparse

from ..items import Product
from ..loaders import ProductLoader

class TescoSpider(scrapy.Spider):
    name = 'tesco'
    download_delay = 0.05
    allowed_domains = ('www.tesco.com',)

    start_urls = (
        'http://www.tesco.com/groceries/',
    )

    def parse(self, response):
        if response.url in self.start_urls:
            return self.parse_start(response)

        elif '/groceries/department/' in response.url:
            return self.parse_primary(response)

        elif '/groceries/product/browse/' in response.url:
            return self.parse_secondary(response)

        elif '/groceries/product/details/' in response.url:
            return self.parse_product(response)

        self.log("Could not parse type of URL")

    def parse_start(self, response):
        for x in response.css('#grocery-navigation li a'):
            name = ' '.join(x.css('::text').extract())

            if name not in (
                "Fresh Food",
                "Bakery",
                "Food Cupboard",
                "Frozen Food",
                "Drinks",
            ):
                self.log("Ignoring primary navigation link %r" % name)
                continue

            yield self._request(response, x)

    def parse_primary(self, response):
        for x in response.css('#superDeptItems li a'):
            name = ' '.join(x.css('::text').extract())

            if name in (
                "Wine",
                "Spirits",
                "Beer & Cider",
            ):
                self.log("Ignoring secondary navigation link: %s" % name)
                continue

            yield self._request(response, x)

    def parse_secondary(self, response):
        # Paginate
        for x in response.css('.controlsBar p.next a'):
            yield self._request(response, x)

        for x in response.css('.productLists li.product h2 a'):
            yield self._request(response, x)

    def parse_product(self, response):
        l = ProductLoader(item=Product(), response=response)

        l.add_css('price', '#productWrapper .linePrice::text')
        l.add_css('name', '#contentMain #productWrapper .desc span::text')
        l.add_css('image_url',
            '#productImages .productImagesList li img::attr(src), '
            '.productDescription .productImage img::attr(src)'
        )

        l.add_value('url', response.url)
        l.add_value('protein_per_100_kcal', response.css(
            '#productWrapper .detailsWrapper table',
        ))

        return l.load_item()

    def _request(self, response, elem):
        url = urlparse.urljoin(
            response.url,
            elem.css('::attr(href)').extract()[0],
        )

        name = ' '.join(elem.css('::text').extract()).strip()
        self.log("Following link labelled %r" % name)

        return scrapy.Request(url, self.parse)
