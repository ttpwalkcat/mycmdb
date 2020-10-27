# -*- conding:utf-8 -*-

import os
import platform
import sys

from plugins.collect_linux_info import collect
# from plugins.collect_windows_info import Win32Info

class InfoCollection(object):

    def collect(self):
        # 收集平台信息
        # 首先判断当前平台，根据平台的不同，执行不同的方法
        try:
            func = getattr(self, platform.system().lower())   # platform.system().lower() 获取系统类型，通过 getattr 方法尝试获取当前 class 中的同名方法，获取失败则说明方法未定义，不支持该类系统
            print(func)
            print(func())
            info_data = func()   # 若上一步执行成功，例如linux，则执行对应的方法linux()，将返回值赋值给 info_data 以便继续加工处理(如果需要)
            print(info_data)
            formatted_data = self.build_report_data(info_data)
            return formatted_data
        except AttributeError:
            sys.exit("不支持当前操作系统：[%s]! " % platform.system())

    @staticmethod
    def linux():
        return collect()

    @staticmethod
    def windows():
        # return Win32Info().collect()
        pass

    @staticmethod
    def build_report_data(data):
        # 留下一个接口，方便以后增加功能或者过滤数据
        pass
        return data

    @staticmethod
    def darwin():
        return "i am darwin"

