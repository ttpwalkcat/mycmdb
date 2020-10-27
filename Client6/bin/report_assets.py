#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json

import os
import sys

BASE_DIR = os.path.dirname(os.getcwd())
# 设置工作目录，使得包和模块能够正常导入
sys.path.append(BASE_DIR)

from conf import settings

def update_test(data):
    """
    创建测试用例
    :param data:
    :return:
    """
    # 将数据打包到一个字典内，并转换为json格式
    data = {"asset_data": json.dumps(data)}
    # 根据settings中的配置，构造url
    url = "http://%s:%s%s" % (settings.Params["server"], settings.Params["port"], settings.Params["url"])
    print("正在将数据发送至: [%s] ......" % url)
    if sys.version_info >= (3,0):
        import urllib.request as request
        import urllib.parse as parse
    else:
        import urllib2 as request
        import urllib as parse

    print("这是 %s 版本" % sys.version_info)

    try:
        # 使用Python内置的urllib.request库，发送post请求。
        # 需要先将数据进行封装，并转换成bytes类型
        data_encode = parse.urlencode(data).encode()
        response = request.urlopen(url=url, data=data_encode, timeout=settings.Params["request_timeout"])
        print("\033[31;1m发送完毕！\033[0m ")
        message = response.read().decode()
        print("返回结果：%s" % message)
    except Exception as e:
        message = "发送失败"
        print("\033[31;1m发送失败，%s\033[0m" % e)


if __name__ == "__main__":

    asset_type_choice = [
        'server',         # '服务器'),
        'networkdevice',  # '网络设备'),
        'storagedevice',  # '存储设备'),
        'securitydevice', # '安全设备'),
        'software',       # '软件资产'),
    ]

    asset_status = [
        0, # '在线'),
        1, # '下线'),
        2, # '未知'),
        3, # '故障'),
        4, # '备用'),
    ]

    server_choice = [
        0, # "PC服务器"),
        1, # "刀片机"),
        2, # "小型机"),
    ]

    security_choice = [
        0, # "防火墙"),
        1, # "入侵检测设备"),
        2, # "互联网网关"),
        4, # "运维审计系统"),
    ]

    storagedevice_choice = [
        0, # "磁盘阵列"),
        1, # "网络存储器"),
        2, # "磁带库"),
        4, # "磁带机"),
    ]

    network_choice = [
        0, # '路由器'),
        1, # "交换机"),
        2, # "负载均衡"),
        4 # "VPN设备"),
    ]

    disk_type_choice = [
        'SATA',
        'SAS',
        'SCSI',
        'SSD',
        'unknown'
    ]

    soft_choice = (
        0, # "操作系统"),
        1, # "办公\开发软件"),
        2 # "业务软件"),
    )

    # 生成 100 条设备记录
    for i in range(0,100):
        sn = "00426-OEM-8992662-1111%s" % str(i).zfill(2)
        asset_type_num = i % 5
        # asset_status_num = i % 5
        # server_choice_num = i % 3
        # security_choice_num = i % 4
        # storagedevice_choice_num = i % 4
        # network_choice_num = i % 4
        # disk_type_choice_num = i % 5
        # sub__choice_num = i % 3


        if asset_type_choice[asset_type_num] == 'server':
            device_data = {
                "asset_type": "server",
                "sub_asset_type": server_choice[i % 3],
                "manufacturer": "innotek GmbH",
                "sn": sn,
                "model": "VirtualBox",
                "uuid": "E8DE611C-4279-495C-9B58-502B6FCED076",
                "wake_up_type": "Power Switch",
                "os_distribution": "Ubuntu",
                "os_release": "Ubuntu 16.04.3 LTS",
                "os_type": "Linux",
                "cpu_count": "2",
                "cpu_core_count": "4",
                "cpu_model": "Intel(R) Core(TM) i5-2300 CPU @ 2.80GHz",
                "ram": [
                    {
                        "slot": "A1",
                        "capacity": 8,
                    }
                ],
                "ram_size": 3.858997344970703,
                "nic": [],
                "physical_disk_driver": [
                    {
                        "model": "VBOX HARDDISK",
                        "size": "50",
                        "sn": "VBeee1ba73-09085302"
                    }
                ]
            }
        elif asset_type_choice[asset_type_num] == 'networkdevice':
            device_data = {
                "asset_type": "networkdevice",
                "sub_asset_type": network_choice[i % 4],
                "manufacturer": "Cisco",
                "sn": sn,
                "model": "思科",
            }
        elif asset_type_choice[asset_type_num] == 'storagedevice':
            device_data = {
                "asset_type": "storagedevice",
                "sub_asset_type": storagedevice_choice[i % 4],
                "manufacturer": "DELL",
                "sn": sn,
                "model": "DELL",
            }
        elif asset_type_choice[asset_type_num] == 'securitydevice':
            device_data = {
                "asset_type": "securitydevice",
                "sub_asset_type": security_choice[i % 4],
                "manufacturer": "Cisco",
                "sn": sn,
                "model": "思科",
            }
        elif asset_type_choice[asset_type_num] == 'software':
            device_data = {
                "asset_type": "software",
                "sub_asset_type": network_choice[i % 4],
                "manufacturer": "Oracle",
                "sn": sn,
                "model": "Oracle",
            }

        update_test(device_data)



#    windows_data = {
#        "os_type": "Windows",
#        "os_release": "7 64bit  6.1.7601 ",
#        "os_distribution": "Microsoft",
#        "asset_type": "server",
#        "cpu_count": 2,
#        "cpu_model": "Intel(R) Core(TM) i5-2300 CPU @ 2.80GHz",
#        "cpu_core_count": 8,
#        "ram": [
#            {
#                "slot": "A1",
#                "capacity": 8,
#                "model": "Physical Memory",
#                "manufacturer": "kingstone ",
#                "sn": "456"
#            },
#
#        ],
#        "manufacturer": "Intel",
#        "model": "P67X-UD3R-B3",
#        "wake_up_type": 6,
#        "sn": "00426-OEM-8992662-111111",
#        "physical_disk_driver": [
#            {
#                "iface_type": "unknown",
#                "slot": 0,
#                "sn": "3830414130423230343234362020202020202020",
#                "model": "KINGSTON SV100S264G ATA Device",
#                "manufacturer": "(标准磁盘驱动器)",
#                "capacity": 128
#            },
#            {
#                "iface_type": "SATA",
#                "slot": 1,
#                "sn": "383041413042323023234362020102020202020",
#                "model": "KINGSTON SV100S264G ATA Device",
#                "manufacturer": "(标准磁盘驱动器)",
#                "capacity": 2048
#            },
#
#        ],
#        "nic": [
#            {
#                "mac": "14:CF:22:FF:48:34",
#                "model": "[00000011] Realtek RTL8192CU Wireless LAN 802.11n USB 2.0 Network Adapter",
#                "name": 11,
#                "ip_address": "192.168.1.110",
#                "net_mask": [
#                    "255.255.255.0",
#                    "64"
#                ]
#            },
#            {
#                "mac": "0A:01:27:00:00:00",
#                "model": "[00000013] VirtualBox Host-Only Ethernet Adapter",
#                "name": 13,
#                "ip_address": "192.168.56.1",
#                "net_mask": [
#                    "255.255.255.0",
#                    "64"
#                ]
#            },
#            {
#                "mac": "14:CF:22:FF:48:34",
#                "model": "[00000017] Microsoft Virtual WiFi Miniport Adapter",
#                "name": 17,
#                "ip_address": "",
#                "net_mask": ""
#            },
#            {
#                "mac": "14:CF:22:FF:48:34",
#                "model": "Intel Adapter",
#                "name": 17,
#                "ip_address": "192.1.1.1",
#                "net_mask": ""
#            },
#
#
#        ]
#    }
#
#
#    linux_data = {
#        "asset_type": "server",
#        "manufacturer": "innotek GmbH",
#        "sn": "00002",
#        "model": "VirtualBox",
#        "uuid": "E8DE611C-4279-495C-9B58-502B6FCED076",
#        "wake_up_type": "Power Switch",
#        "os_distribution": "Ubuntu",
#        "os_release": "Ubuntu 16.04.3 LTS",
#        "os_type": "Linux",
#        "cpu_count": "2",
#        "cpu_core_count": "4",
#        "cpu_model": "Intel(R) Core(TM) i5-2300 CPU @ 2.80GHz",
#        "ram": [
#            {
#                "slot": "A1",
#                "capacity": 8,
#            }
#        ],
#        "ram_size": 3.858997344970703,
#        "nic": [],
#        "physical_disk_driver": [
#            {
#                "model": "VBOX HARDDISK",
#                "size": "50",
#                "sn": "VBeee1ba73-09085302"
#            }
#        ]
#    }
#
#    update_test(linux_data)
#    update_test(windows_data)