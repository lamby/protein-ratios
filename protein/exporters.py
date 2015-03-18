import cgi

from scrapy.contrib.exporter import JsonItemExporter

class ProteinJsonItemExporter(JsonItemExporter):
    def export_item(self, item):
        if self.first_item:
            self.first_item = False
        else:
            self.file.write(',\n')

        self.file.write(self.encoder.encode([
            '<a href="%s"><div class="image" style="background-image: url(%s);"/></a>' % (
                cgi.escape(item['url']),
                cgi.escape(item['image_url']),
            ),
            '<a href="%s">%s</a>' % (
                cgi.escape(item['url']),
                cgi.escape(item['name']),
            ),
            cgi.escape(item.get('size', '')),
            '&pound;%s' % cgi.escape(item['price']),
            '%.2f' % item['protein_per_100_kcal'],
        ]))
