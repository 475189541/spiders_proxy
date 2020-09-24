import scrapy, redis
from spiders_proxy.items import SpidersProxyItem
from spiders_proxy.settings import redis_host, redis_password, redis_port


class SpidersAnalysisProxySpider(scrapy.Spider):
    name = 'spiders_analysis_proxy'
    allowed_domains = ['httpbin.org', 'www.xicidaili.com', 'www.data5u.com', 'www.66daili.cn', 'www.goubanjia.com']
    custom_settings = {
        'ITEM_PIPELINES': {'spiders_proxy.pipelines.SpidersProxyPipeline': 300},
        'DOWNLOADER_MIDDLEWARES': {'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': None,
                                   'spiders_proxy.middlewares.HttpbinProxyMiddleware': 543},
        'RETRY_ENABLED': False,
        # 'RETRY_TIMES': 1,
        'HTTPERROR_ALLOWED_CODES': [500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 302],
        'RANDOMIZE_DOWNLOAD_DELAY': False,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY ': 2,
        # 'LOG_LEVEL': 'WARNING',
        'LOG_LEVEL': 'WARNING',
    }

    def __init__(self, **kwargs):
        super(SpidersAnalysisProxySpider, self).__init__()
        self.httpbin_url = 'http://httpbin.org/ip'
        self.httpsbin_url = 'https://httpbin.org/ip'
        self.redis_connection = redis.Redis(host=redis_host, password=redis_password, port=redis_port, db=1)

    def analysis_proxy(self, ip_type, ip, port):
        proxy = '%s://%s:%s' % (ip_type, ip, port)
        url = self.httpsbin_url if ip_type == 'https' else self.httpbin_url
        meta = {'proxy': proxy, 'download_slot': proxy}
        request = scrapy.Request(url=url, dont_filter=True, callback=self.parse_analysis, meta=meta)
        return request

    def start_requests(self):
        yield scrapy.Request(url=self.httpbin_url, callback=self.parse_redis_analysis, dont_filter=True, meta={'download_slot': self.httpbin_url})

    def parse_redis_analysis(self, response):
        if response.status not in self.custom_settings['HTTPERROR_ALLOWED_CODES']:
            url = response.url
            proxy_set = self.redis_connection.smembers('proxy')
            for proxy in proxy_set:
                p = proxy.decode('utf-8')
                dumps_list = p.split(':')
                request = self.analysis_proxy(ip_type=dumps_list[0], ip=dumps_list[1].strip('/'), port=dumps_list[2])
                yield request
            yield scrapy.Request(url=url, dont_filter=True, callback=self.parse_redis_analysis, meta={'download_slot': url})

    def parse_analysis(self, response):
        if response.status not in self.custom_settings['HTTPERROR_ALLOWED_CODES']:
            proxy = response.meta['proxy']
            item = SpidersProxyItem()
            item['proxy'] = proxy
            yield item


