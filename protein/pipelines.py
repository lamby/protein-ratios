from scrapy.exceptions import DropItem

class EnsureMetadata(object):
    def process_item(self, item, spider):
        if 'price' not in item:
            raise DropItem("Item is unavailable")

        if 'protein_per_100_kcal' not in item:
            raise DropItem("Did not parse nutrition data") 

        return item
