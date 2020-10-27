# -*- coding:utf-8 -*-


import json
import time
import sys
# import urllib.parse
# import urllib.request
from core import info_collection
from conf import settings


class ArgvHandler(object):

    def __init__(self, args):
        self.args = args
        self.parse_args()

    def parse_args(self):
        """
        分析参数，如果有参数指定的方法，则执行该功能，如果没有，打印帮助说明
        :return:
        """
        if len(self.args) > 1 and hasattr(self, self.args[1]):
            func = getattr(self, self.args[1])
            func()
        else:
            self.help_msg()

    @staticmethod
    def help_msg():
        """
        帮助说明
        :return:
        """
        msg = '''
        参数名               功能

        collect_data        测试收集硬件信息的功能

        report_data         收集硬件信息并汇报
        '''
        print(msg)

    @staticmethod
    def collect_data():
        """  收集硬件信息，用于测试"""
        info = info_collection.InfoCollection()
        asset_data = info.collect()
        print(asset_data)

    @staticmethod
    def report_data():
        """
        收集硬件信息，然后发送到服务器。
        :return:
        """
        # 收集信息
        info = info_collection.InfoCollection()
        asset_data = info.collect()
        # 将数据打包到一个字典内，并转换为 json 格式
        data = {"asset_data": json.dumps(asset_data)}
        # 根据 settings 中的配置，构造URL
        url = "http://%s:%s%s" % (settings.Params['server'], settings.Params['port'], settings.Params['url'])
        print('正在将数据发送至：[%s] ......' % url)

        """
        Python2 中 urllib 的 urlencode 在 Python3 中分别拆分到 urllib.parse；
        urllib2 的 urlopen 拆分到 urllib.request
        因此，需要判断当前 Python 版本，并导入对应的库
        """
        if sys.version_info >= (3, 0):
            import urllib.request as request
            import urllib.parse as parse
        else:
            import urllib2 as request
            import urllib as parse

        try:
            # 使用 Python 内置的 urllib.request库，发送 post 请求。
            # 需要先将数据进行封装，并转换成bytes 类型（这里urlencode处理的数据用作 POST操作，必须编码为bytes，否则将导致TypeError）

            data_encode = parse.urlencode(data).encode()
            response = request.urlopen(url=url, data=data_encode, timeout=settings.Params['request_timeout'])

            print("\033[31;1m发送完毕！\033[0m")
            message = response.read().decode() if sys.version_info >= (3, 0) else response.read()# if isinstance(response.read(), bytes) else response.read()
            print("返回结果：%s" % message )
        except Exception as e:
            message = "发送失败" + "  错误原因：{}".format(e)
            print("\033[31;1m发送失败，错误原因：%s\033[0m" % e)

        # 记录发送日志
        with open(settings.PATH, 'ab') as f:
            log = "发送时间：%s \t 服务器地址： %s \t 返回结果：%s \n" % (time.strftime("%Y-%m-%d %H:%M:%S"), url, message)
            log = log.encode() if sys.version_info >= (3, 0) else log
            f.write(log)
            print("日志记录成功")