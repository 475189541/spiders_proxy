import os, sys, argparse, importlib, pkgutil
from functools import reduce
from scrapy.cmdline import execute

# 设置工程的目录，可以在任何路径下运行execute
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy", "crawl", 'spiders_http_proxy'])


if __name__ == '__main__':
    module_dir = 'spiders_proxy/spiders'
    prefix = 'spiders_proxy.spiders.'
    modules = [importlib.import_module(c.name) for c in pkgutil.iter_modules([module_dir], prefix=prefix)]
    parser = argparse.ArgumentParser(description='启动配置')
    parser.add_argument('-l', type=str, default='', help='-l lsname or -l lsn 查看所有 爬虫名字')
    parser.add_argument('-n', type=str, default=None, help=' 爬虫名字')
    args = parser.parse_args()
    if args.l.lower() in ['lsname', 'lsn']:
        modules_iter = map(lambda x: list(map(lambda y: f'-n {y[1].name}', filter(lambda f: isinstance(f[1], type) and hasattr(f[1], 'name'), x.__dict__.items()))), modules)
        modules_name = set(reduce(lambda a, b: a + b, modules_iter))
        print('\n'.join(modules_name))
    if args.n:
        execute(["scrapy", "crawl", args.n])

