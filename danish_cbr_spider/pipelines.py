# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import logging
from typing import Dict

import pymongo


class TranslatorPipeline(object):
    translations: Dict[str, str]

    def __init__(self):
        with open("anal/translations.json") as f:
            self.translations = json.load(f)

    @staticmethod
    def _translate_keys(obj, translations: Dict[str, str]):
        ty = type(obj)
        if ty is list:
            return [TranslatorPipeline._translate_keys(obj, translations) for obj in obj]
        elif ty is dict:
            obj: dict
            res = dict()
            for k, v in obj.items():
                k = translations.get(k, k)
                res[k] = TranslatorPipeline._translate_keys(v, translations)
            return res

        elif ty in [str, int, bool, float, type(None)]:
            return obj
        else:
            raise RuntimeError(f"Don't know how to handle type {ty}")

    def process_item(self, item, _spider):
        return TranslatorPipeline._translate_keys(item, self.translations)


class MongoDBPipeline(object):
    collection_name = 'companies'
    client: pymongo.MongoClient
    db: pymongo.mongo_client.database.Database

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'danish_companies')
        )

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.logger = logging.getLogger('MongoDBPipeline')

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    @property
    def collection(self):
        return self.db[self.collection_name]

    def process_item(self, item, _spider):
        self.collection.insert_one(dict(item))
        self.logger.debug("Inserted item into mongodb")
        return item
