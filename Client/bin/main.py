#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
完全可以吧客户端信息收集脚本做成 Windows 和 Linux 两个不同的版本
"""
import os
import sys


BASE_DIR = os.path.dirname(os.getcwd())
# print(os.getcwd())
# print(BASE_DIR)
# 设置工作目录，使得包和模块能够正常导入
sys.path.append(BASE_DIR)

from core import handler

if __name__ == "__main__":
    handler.ArgvHandler(sys.argv)
