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
        'RANDOMIZE_DOWNLOAD_DELAY': False,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY ': 2,
        'DOWNLOAD_TIMEOUT': 15,
        # 'LOG_LEVEL': 'WARNING',
        'LOG_LEVEL': 'WARNING',
    }

    def __init__(self, **kwargs):
        super(SpidersHttpProxySpider, self).__init__()
        self.httpbin_url = 'http://httpbin.org/ip'
        self.httpsbin_url = 'https://httpbin.org/ip'
        self.redis_connection = redis.Redis(host=redis_host, password=redis_password, port=redis_port, db=1)
        self.data5u_code_table = {chr(c): int(i) for i, c in enumerate(list(range(65, 91)))}

    def analysis_proxy(self, ip_type, ip, port):
        proxy = '%s://%s:%s' % (ip_type, ip, port)
        url = self.httpsbin_url if ip_type == 'https' else self.httpbin_url
        meta = {'proxy': proxy, 'download_slot': proxy}
        request = scrapy.Request(url=url, dont_filter=True, callback=self.parse_analysis, meta=meta)
        return request

    def start_requests(self):
        # xici_url_list = [['https://www.xicidaili.com/nn/%s' % i, self.parse_xicidaili] for i in range(1, 3)]
        url_list = [
            ['http://www.data5u.com', self.parse_data5u],
            ['http://www.goubanjia.com/', self.parse_goubanjia],
        ] + [[f'http://www.66daili.cn/showProxySingle/{i}/', self.parse_66ip] for i in range(6125, 10, -1)]
        for url in url_list:
            yield scrapy.Request(url=url[0], callback=url[1], dont_filter=True, meta={'download_slot': url[0]})

    def parse_data5u(self, response):
        if response.status not in self.custom_settings['HTTPERROR_ALLOWED_CODES']:
            tr_tree = response.xpath('//ul[@class="l2"]')
            for tr in tr_tree:
                ip_type = tr.xpath('./span[4]/li/text()').extract_first().strip().lower()
                ip = tr.xpath('./span[1]/li/text()').extract_first().strip()
                code = tr.xpath('./span[2]/li/@class').extract_first().strip().lstrip('port').strip()
                port_dumps = int(''.join([str(self.data5u_code_table[c]) if self.data5u_code_table[c] < 10 else '9' for c in code])) / 8
                port = int(port_dumps) if port_dumps <= 9999 else 9999
                request = self.analysis_proxy(ip_type=ip_type, ip=ip, port=port)
                yield request
            yield scrapy.Request(url=response.url, callback=self.parse_data5u, dont_filter=True, meta={'download_slot': response.url})

    def parse_66ip(self, response):
        if response.status not in self.custom_settings['HTTPERROR_ALLOWED_CODES']:
            result_list = response.xpath('//article/table/tbody/tr')
            for result in result_list:
                ip = result.xpath('./th/text()').extract_first()
                port = result.xpath('./td[1]/text()').extract_first()
                request = self.analysis_proxy(ip_type='http', ip=ip, port=port)
                yield request
                request = self.analysis_proxy(ip_type='https', ip=ip, port=port)
                yield request
            yield scrapy.Request(url=response.url, callback=self.parse_66ip, dont_filter=True, meta={'download_slot': response.url})

    def parse_xicidaili(self, response):
        if response.status not in self.custom_settings['HTTPERROR_ALLOWED_CODES']:
            tr_list = response.xpath('//table[@id="ip_list"]/tr[@class]')
            for tr in tr_list:
                ip = tr.xpath('./td[2]/text()').extract_first()
                port = tr.xpath('./td[3]/text()').extract_first()
                ip_type = tr.xpath('./td[6]/text()').extract_first().lower()
                request = self.analysis_proxy(ip_type=ip_type, ip=ip, port=port)
                yield request
            yield scrapy.Request(url=response.url, callback=self.parse_xicidaili, dont_filter=True, meta={'download_slot': response.url})

    def parse_goubanjia(self, response):
        if response.status not in self.custom_settings['HTTPERROR_ALLOWED_CODES']:
            tr_tree = response.xpath('//table[@class="table table-hover"]/tbody/tr')
            for tr in tr_tree:
                ip_type = ''.join(tr.xpath('./td[3]//text()').extract()).strip().lower()
                ip = ''.join(map(lambda x: x.xpath('./text()').extract_first(''), filter(lambda f: not f.xpath('./@style').extract_first('').endswith('none;') and not f.xpath('./@class').extract_first('').startswith('port'), tr.xpath('./td[@class="ip"]/*'))))
                code = tr.xpath('./td[@class="ip"]/span[starts-with(@class, "port")]/@class').extract_first().strip().lstrip('port').strip()
                port_dumps = int(''.join([str(self.data5u_code_table[c]) if self.data5u_code_table[c] < 10 else '9' for c in code])) / 8
                port = int(port_dumps) if port_dumps <= 9999 else 9999
                request = self.analysis_proxy(ip_type=ip_type, ip=ip, port=port)
                yield request
            yield scrapy.Request(url=response.url, callback=self.parse_goubanjia, dont_filter=True, meta={'download_slot': response.url})

    def parse_analysis(self, response):
        if response.status not in self.custom_settings['HTTPERROR_ALLOWED_CODES']:
            proxy = response.meta['proxy']
            item = SpidersProxyItem()
            item['proxy'] = proxy
            yield item


