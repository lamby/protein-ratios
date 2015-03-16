import scrapy

class Product(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    image_url = scrapy.Field()
    protein_per_100_kcal = scrapy.Field()
