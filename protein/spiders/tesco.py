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

    navigation = {
        "Fresh Food": {
            'filter': None,
        },
        "Bakery": {
            'filter': None,
        },
        "Food Cupboard": {
            'filter': None,
        },
        "Frozen Food": {
            'filter': None,
        },
        "Drinks": {
            'filter': 'blacklist',
            'values': (
                "Wine",
                "Spirits",
                "Beer & Cider",
            ),
        },
        "Health & Beauty": {
            'filter': 'whitelist',
            'values': (
                "Healthcare",
            ),
        },
    }

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

            if name not in self.navigation:
                self.log("Ignoring primary navigation link %r" % name)
                continue

            yield self._request(response, x)

    def parse_primary(self, response):
        primary_name = ' '.join(response.css('h1#intro::text').extract())

        try:
            config = self.navigation[primary_name]
        except KeyError:
            self.log("No configuration for primary %r" % primary_name)
            return

        filter_ = config['filter']

        for x in response.css('#superDeptItems li a'):
            name = ' '.join(x.css('::text').extract())

            if filter_ == 'whitelist' and name not in config['values']:
                self.log("Ignoring %r in %r as it's not in whitelist" % (
                    name,
                    primary_name,
                ))
                continue

            if filter_ == 'blacklist' and name in config['values']:
                self.log("Ignoring %r in %r as it's blacklisted" % (
                    name,
                    primary_name,
                ))
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
