# scrapy_proxy
### 基于Scrapy 1.5.1的Python3.6 代理ip池爬虫 

+ settings.py: Scrapy默认设置。
+ middlewares.py: 重试中间件。用于处理redis中的ip
+ spiders_http_proxy.py: 爬虫程序。
+ starts.py: 调试启动文件入口。
+ 欢迎有能力的开发者共同维护，半年之内此项目我还会继续跟进。
+ 问题和讨论可以发到我的邮箱475189541@qq.com。
+ 爬虫环境部署于linux环境，windows环境下的问题不予解答。

### 实现功能
```
1.9大免费网站的代理IP爬取
2.每秒钟扫描一遍redis将过期的ip去除
3.爬取时只保留可用的代理IP
4.最高可爬取1000条代理ip
5.代码中很少使用外部库，方便部署安装。
```


### 使用教程

#### 1.运行前你需要安装并配置好环境：

+ Python 3.6
+ Scrapy
+ curl
+ redis

#### 2.环境安装

+ 切换至与requirements.txt同级目录
+ pip install -r requirements.txt
+ sudo apt-get install -y curl
+ sudo apt-get install redis-server

#### 3.调试运行

+ 启动redis服务
+ 切换至与starts.py同级目录下
+ 终端命令行键入python starts.py

#### 4.部署运行(Linux)

+ 启动redis服务
+ 终端命令行键入scrapydart
+ 打开一个新的终端 切换至starts.py同级目录下 命令行键入scrapyd-deploy -p scrapy_proxy
+ 打开浏览器，输入地址　http://localhost:6800/
+ curl http://localhost:6800/schedule.json -d project=scrapy_proxy -d spider=spiders_http_proxy

#### ５.部署运行(Windows)

+ 与Linux类似，但是坑较多，不予解答


