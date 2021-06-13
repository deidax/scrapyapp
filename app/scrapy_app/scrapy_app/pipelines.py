# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from main.models import Product


class ScrapyAppPipeline(object):
    def process_item(self, item, spider):
        # Product = Product(manufacturer=item.get('manufacturer'), brand=item.get('brand'), name=item.get('name'), description=item.get('description'), url=item.get('url'))
        # Product.save()
        return item
