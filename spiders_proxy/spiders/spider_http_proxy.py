import scrapy, redis
from spiders_proxy.items import SpidersProxyItem
from spiders_proxy.settings import redis_host, redis_password, redis_port


class SpidersHttpProxySpider(scrapy.Spider):
    name = 'spiders_http_proxy'
    allowed_domains = ['httpbin.org', 'www.xicidaili.com', 'www.data5u.com', 'www.66daili.cn', 'www.goubanjia.com']
    custom_settings = {
        'ITEM_PIPELINES': {'spiders_proxy.pipelines.SpidersProxyPipeline': 300},
        'DOWNLOADER_MIDDLEWARES': {'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': None,
                                   'spiders_proxy.middlewares.HttpbinProxyMiddleware': 543},
        'RETRY_ENABLED': False,
        # 'RETRY_TIMES': 1,
        'HTTPERROR_ALLOWED_CODES': [500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510],
        'DOWNLOAD_DELAY ': 1,
        'DOWNLOAD_TIMEOUT': 2,
        # 'LOG_LEVEL': 'WARNING',
        'LOG_LEVEL': 'ERROR',
    }

    def __init__(self, **kwargs):
        super(SpidersHttpProxySpider, self).__init__()
        self.httpbin_url = 'http://httpbin.org/ip'
        self.redis_connection = redis.Redis(host=redis_host, password=redis_password, port=redis_port, db=1)

    def analysis_proxy(self, ip_type, ip, port):
        proxy = '%s://%s:%s' % (ip_type, ip, port)
        request = scrapy.Request(url=self.httpbin_url, dont_filter=True, callback=self.parse_analysis, meta={'proxy': proxy})
        return request

    def start_requests(self):
        yield scrapy.Request(url=self.httpbin_url, dont_filter=True, callback=self.parse_redis_analysis)
        xici_url_list = [['https://www.xicidaili.com/nn/%s' % i, self.parse_xicidaili] for i in range(1, 3924)]
        url_list = [
            ['http://www.data5u.com', self.parse_data5u],
            ['http://www.66daili.cn/showProxySingle/4588/', self.parse_66ip],
            ['http://www.66daili.cn/showProxySingle/4587/', self.parse_66ip],
            ['http://www.goubanjia.com/', self.parse_goubanjia],
        ]
        for url in url_list:
            yield scrapy.Request(url=url[0], callback=url[1], dont_filter=True)

    def parse_redis_analysis(self, response):
        if response.status not in self.custom_settings['HTTPERROR_ALLOWED_CODES']:
            proxy_set = self.redis_connection.smembers('proxy')
            for proxy in proxy_set:
                p = proxy.decode('utf-8')
                dumps_list = p.split(':')
                request = self.analysis_proxy(ip_type=dumps_list[0], ip=dumps_list[1].strip('/'), port=dumps_list[2])
                yield request
            yield scrapy.Request(url=response.url, dont_filter=True, callback=self.parse_redis_analysis)

    def parse_data5u(self, response):
        if response.status not in self.custom_settings['HTTPERROR_ALLOWED_CODES']:
            tr_tree = response.xpath('//ul[@class="l2"]')
            for tr in tr_tree:
                ip_type = tr.xpath('./span[4]/li/text()').extract_first().strip().lower()
                ip = tr.xpath('./span[1]/li/text()').extract_first().strip()
                port = tr.xpath('./span[2]/li/text()').extract_first().strip()
                request = self.analysis_proxy(ip_type=ip_type, ip=ip, port=port)
                yield request
            yield scrapy.Request(url=response.url, callback=self.parse_data5u, dont_filter=True)

    def parse_66ip(self, response):
        if response.status not in self.custom_settings['HTTPERROR_ALLOWED_CODES']:
            result_list = response.xpath('//article/table/tbody/tr')
            for result in result_list:
                ip = result.xpath('./th/text()').extract_first()
                port = result.xpath('./td[1]/text()').extract_first()
                request = self.analysis_proxy(ip_type='http', ip=ip, port=port)
                yield request
            yield scrapy.Request(url=response.url, callback=self.parse_66ip, dont_filter=True)

    def parse_xicidaili(self, response):
        if response.status not in self.custom_settings['HTTPERROR_ALLOWED_CODES']:
            tr_list = response.xpath('//table[@id="ip_list"]/tr[@class]')
            for tr in tr_list:
                ip = tr.xpath('./td[2]/text()').extract_first()
                port = tr.xpath('./td[2]/text()').extract_first()
                ip_type = tr.xpath('./td[6]/text()').extract_first().lower()
                request = self.analysis_proxy(ip_type=ip_type, ip=ip, port=port)
                yield request
            yield scrapy.Request(url=response.url, callback=self.parse_xicidaili, dont_filter=True)

    def parse_goubanjia(self, response):
        if response.status not in self.custom_settings['HTTPERROR_ALLOWED_CODES']:
            tr_tree = response.xpath('//tr[@class="warning"]')
            for tr in tr_tree:
                ip_type = ''.join(tr.xpath('./td[3]//text()').extract()).strip().lower()
                td_text = ''.join(tr.xpath('./td[1]//text()').extract()).strip().split(':')
                if len(td_text) > 1:
                    ip = td_text[0]
                    port = td_text[1]
                    request = self.analysis_proxy(ip_type=ip_type, ip=ip, port=port)
                    yield request
            yield scrapy.Request(url=response.url, callback=self.parse_goubanjia, dont_filter=True)

    def parse_analysis(self, response):
        if response.status not in self.custom_settings['HTTPERROR_ALLOWED_CODES']:
            proxy = response.meta['proxy']
            item = SpidersProxyItem()
            item['proxy'] = proxy
            yield item


