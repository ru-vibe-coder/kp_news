# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
import requests
import base64
from itemadapter import ItemAdapter

class MongoDBPipeline:
    collection_name = "news"

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI", "mongodb://localhost:27017"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "kp_news"),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        return item

class PhotoDownloaderPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        url = adapter.get('header_photo_url')

        if not url:
            adapter['header_photo_base64'] = 'Нет фото'
            return item

        try:
            spider.logger.info(f"📸 Скачиваю фото: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            encoded = base64.b64encode(response.content).decode('utf-8')
            adapter['header_photo_base64'] = encoded
        except Exception as e:
            spider.logger.warning(f"⚠️ Не удалось скачать фото {url}: {e}")
            adapter['header_photo_base64'] = ''

        return item
