BOT_NAME = 'protein'

SPIDER_MODULES = ('protein.spiders',)
NEWSPIDER_MODULE = 'protein.spiders'

ITEM_PIPELINES = {
    'protein.pipelines.EnsureMetadata': 100,
}

FEED_EXPORTERS = {
    'proteinjson': 'protein.exporters.ProteinJsonItemExporter',
}
