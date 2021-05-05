import time
import json
import requests
from bs4 import BeautifulSoup
from taskflow import engines
from taskflow.patterns import linear_flow
from taskflow.task import Task

REQUEST_HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Cache-Control': 'max-age=0',
    'Host': 'data.10jqka.com.cn',
    'Cookie': 'v=A3FpndfstQnfehkd4jPKdzxJgPYIXuXQj9KJ5FOGbThXep9gm671oB8imbXg'
}


class MoneyFlowDownload(Task):
    """
    下载资金流数据
    数据源地址：http://data.10jqka.com.cn/funds/gnzjl/
    """
    BASE_URl = {
        # "gg": 'http://data.10jqka.com.cn/funds/ggzjl/field/tradezdf/order/desc/page/%s',
        "gn": 'http://data.10jqka.com.cn/funds/gnzjl/field/tradezdf/order/desc/page/%s/ajax/1/free/1/',
        "hy": 'http://data.10jqka.com.cn/funds/hyzjl/field/tradezdf/order/desc/page/%s'
    }

    def execute(self, bizdate, *args, **kwargs):

        for name, base_url in self.BASE_URl.items():
            # 爬取数据的存储路径
            dt_path = r'/home/zhf/github/MA10Test/MA10Test/test/%s_%s.csv' % (bizdate, name)

            with open(dt_path, "a+") as f:
                # 记录数据文件的当前位置
                pos = f.tell()
                f.seek(0)
                lines = f.readlines()
                # 读取文件中的全部数据并将第一列存储下来作为去重依据，防止爬虫意外中断后重启程序时，重复写入相同
                crawled_list = list(map(lambda line: line.split(",")[0], lines))
                f.seek(pos)
                fail_count = 0
                # 循环500次，从第一页开始爬取数据，当页面没有数据时终端退出循环
                for i in range(1, 500):
                    if fail_count > 10:
                        break
                    print("start crawl %s, %s" % (name, base_url % i))
                    web_source = requests.get(base_url % i, headers=REQUEST_HEADER)
                    soup = BeautifulSoup(web_source.content.decode("gbk"), 'lxml')
                    try:
                        table = soup.select('.J-ajax-table')[0]
                        tbody = table.select('tbody tr')
                        # 当tbody为空时，则说明当前页已经没有数据了，此时终止循环
                        if len(tbody) == 0:
                            break
                        for tr in tbody:
                            fields = tr.select('td')
                            # 将每行记录第一列去掉，第一列为序号，没有存储必要
                            record = [field.text.strip() for field in fields[1:]]
                            # 如果记录还没有写入文件中，则执行写入操作，否则跳过这行写入
                            if record[0] not in crawled_list:
                                f.writelines([','.join(record) + '\n'])
                        # 同花顺网站有反爬虫的机制，爬取速度过快很可能被封
                        time.sleep(1)
                    except:
                        print("No.%d get data failed." % i)
                        fail_count += 1
                        continue


if __name__ == '__main__':
    bizdate = '20210122'
    tasks = [
        MoneyFlowDownload('moneyflow data download')
    ]
    flow = linear_flow.Flow('ths data download').add(*tasks)
    e = engines.load(flow, store={'bizdate': bizdate})
    e.run()
