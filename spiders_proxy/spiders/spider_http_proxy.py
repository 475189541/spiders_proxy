import scrapy
import re
import redis
from spiders_proxy.items import SpidersProxyItem


class SpidersHttpProxySpider(scrapy.Spider):
    name = 'spiders_http_proxy'
    allowed_domains = ['www.bilibili.com']
    custom_settings = {
        'ITEM_PIPELINES': {'spiders_proxy.pipelines.SpidersProxyPipeline': 300},
        'DOWNLOADER_MIDDLEWARES': {'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': None,
                                   'spiders_proxy.middlewares.HttpbinProxyMiddleware': 502},
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 2,
        'HTTPERROR_ALLOWED_CODES': [500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510],
        'DOWNLOAD_TIMEOUT': 3,
        'DOWNLOAD_DELAY ': 3,
        'LOG_LEVEL': 'ERROR',
    }

    def __init__(self, **kwargs):
        super(SpidersHttpProxySpider, self).__init__()
        self.pattern_66ip = re.compile('[\s](.*?)<br')
        self.bilibili_url = 'http://httpbin.org/ip'
        self.redis_connection = redis.Redis(host='127.0.0.1', password='gannicus', port=6379, db=1)

    def analysis_proxy(self, ip_type, ip, port):
        proxy = '%s://%s:%s' % (ip_type, ip, port)
        request = scrapy.Request(url=self.bilibili_url, dont_filter=True, callback=self.parse_analysis, meta={'proxy': proxy})
        return request

    def start_requests(self):
        url_baidu = 'https://www.baidu.com/'
        yield scrapy.Request(url=url_baidu, dont_filter=True, callback=self.parse_redis_analysis)

        # ip3366_list = list(map(lambda x: ['http://www.ip3366.net/free/?stype=1&page=%s' % x, self.parse_ip3366], range(1, 8)))
        jiangxianli_list = list(map(lambda x: ['http://ip.jiangxianli.com/?page=%s' % x, self.parse_jiangxianli], range(1, 7)))
        url_list = [
            ['http://www.data5u.com/free/gngn/index.shtml', self.parse_data5u],
            ['http://www.66ip.cn/mo.php', self.parse_66ip],
            # ['https://www.xicidaili.com/nn/', self.parse_xicidaili],
            ['http://www.goubanjia.com/', self.parse_goubanjia],
            ['https://www.kuaidaili.com/free/inha/', self.parse_kuaidaili],
            ['http://www.iphai.com/free/ng', self.parse_iphai],
            ['http://31f.cn/http-proxy/', self.parse_31f],
            ['http://31f.cn/https-proxy/', self.parse_31f],
        ]
        urls = jiangxianli_list + url_list
        for url in urls:
            yield scrapy.Request(url=url[0], callback=url[1], dont_filter=True)

    def parse_redis_analysis(self, resposne):
        proxy_set = self.redis_connection.smembers('proxy')
        for proxy in proxy_set:
            p = proxy.decode('utf-8')
            yield scrapy.Request(url=self.bilibili_url, dont_filter=True, callback=self.analysis_redis, meta={'proxy': p})
        yield scrapy.Request(url=resposne.url, dont_filter=True, callback=self.parse_redis_analysis)

    def analysis_redis(self, response):
        proxy = response.meta['proxy']
        # log.msg('代理正常: %s ' % proxy, level=log.ERROR)

    def parse_ip3366(self, response):
        tr_tree = response.xpath('//tbody//tr')
        for tr in tr_tree:
            ip_type = tr.xpath('./td[4]/text()').extract_first().strip().lower()
            ip = tr.xpath('./td[1]/text()').extract_first().strip()
            port = tr.xpath('./td[2]/text()').extract_first().strip()
            request = self.analysis_proxy(ip_type=ip_type, ip=ip, port=port)
            yield request
        yield scrapy.Request(url=response.url, callback=self.parse_ip3366, dont_filter=True)

    def parse_jiangxianli(self, response):
        tr_tree = response.xpath('//tbody//tr')
        for tr in tr_tree:
            ip_type = tr.xpath('./td[5]/text()').extract_first().strip().lower()
            ip = tr.xpath('./td[2]/text()').extract_first().strip()
            port = tr.xpath('./td[3]/text()').extract_first().strip()
            request = self.analysis_proxy(ip_type=ip_type, ip=ip, port=port)
            yield request
        yield scrapy.Request(url=response.url, callback=self.parse_jiangxianli, dont_filter=True)

    def parse_data5u(self, response):
        tr_tree = response.xpath('//ul[@class="l2"]')
        for tr in tr_tree:
            ip_type = tr.xpath('./span[4]/li/text()').extract_first().strip().lower()
            ip = tr.xpath('./span[1]/li/text()').extract_first().strip()
            port = tr.xpath('./span[2]/li/text()').extract_first().strip()
            request = self.analysis_proxy(ip_type=ip_type, ip=ip, port=port)
            yield request
        yield scrapy.Request(url=response.url, callback=self.parse_data5u, dont_filter=True)

    def parse_66ip(self, response):
        result_list = map(lambda x: x.strip().split(':'), self.pattern_66ip.findall(response.text, re.S))
        for result in result_list:
            request = self.analysis_proxy(ip_type='http', ip=result[0], port=result[1])
            yield request
        yield scrapy.Request(url=response.url, callback=self.parse_66ip, dont_filter=True)

    def parse_xicidaili(self, response):
        pass

    def parse_goubanjia(self, response):
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

    def parse_kuaidaili(self, response):
        tr_tree = response.xpath('//tbody/tr')
        for tr in tr_tree:
            ip_type = tr.xpath('./td[4]/text()').extract_first().strip().lower()
            ip = tr.xpath('./td[1]/text()').extract_first().strip()
            port = tr.xpath('./td[2]/text()').extract_first().strip()
            request = self.analysis_proxy(ip_type=ip_type, ip=ip, port=port)
            yield request
        yield scrapy.Request(url=response.url, callback=self.parse_kuaidaili, dont_filter=True)

    def parse_iphai(self, response):
        tr_tree = response.xpath('//div[@class="table-responsive module"]/table/tr')
        for tr in tr_tree:
            th = tr.xpath('./th').extract()
            if th:
                continue
            # ip_type = ''.join(tr.xpath('./td[4]//text()').extract()).strip().lower()
            ip = ''.join(tr.xpath('./td[1]//text()').extract()).strip()
            port = ''.join(tr.xpath('./td[2]//text()').extract()).strip()
            request = self.analysis_proxy(ip_type='http', ip=ip, port=port)
            yield request
        yield scrapy.Request(url=response.url, callback=self.parse_iphai, dont_filter=True)

    def parse_31f(self, response):
        tr_tree = response.xpath('//table/tr')
        for tr in tr_tree:
            th = tr.xpath('./th').extract()
            if th:
                continue
            # ip_type = ''.join(tr.xpath('./td[4]//text()').extract()).strip().lower()
            ip = ''.join(tr.xpath('./td[2]//text()').extract()).strip()
            port = ''.join(tr.xpath('./td[3]//text()').extract()).strip()
            request = self.analysis_proxy(ip_type='http', ip=ip, port=port)
            yield request
        yield scrapy.Request(url=response.url, callback=self.parse_31f, dont_filter=True)

    def parse_analysis(self, response):
        item = SpidersProxyItem()
        proxy = response.meta['proxy']
        item['proxy'] = proxy
        yield item
        # log.msg('代理正常: %s ' % proxy, level=log.ERROR)


