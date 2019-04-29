# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from .items import SpidersProxyItem


class SpidersProxyPipeline(object):

    def __init__(self):
        super(SpidersProxyPipeline, self).__init__()

    def process_item(self, item, spider):
        if isinstance(item, SpidersProxyItem):
            spider.redis_connection.sadd('proxy', item['proxy'])

        return item
