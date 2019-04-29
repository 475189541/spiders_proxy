import os
import sys
from scrapy.cmdline import execute

# 设置工程的目录，可以在任何路径下运行execute
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", "spiders_http_proxy"])

#
# import redis
# import requests
#
#
# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',}
# url = 'https://www.bilibili.com/'
# session = requests.Session()
# redis_connection = redis.Redis(host='127.0.0.1', password='gannicus', port=6379, db=1)
# proxy_set = redis_connection.smembers('proxy')
# for num, proxy in enumerate(proxy_set):
#     proxy_str = proxy.decode('utf-8')
#     proxies = {'http': proxy_str}
#     response = requests.get(url, proxies=proxies, headers=headers)
#     print(num, response.status_code, proxy_str)

