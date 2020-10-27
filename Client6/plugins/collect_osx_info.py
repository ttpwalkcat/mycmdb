#!/usr/bin/env python
# -*- coding:utf-8 -*-

import subprocess


def collect():
    filter_keys = ["Manufacturer", "Serial Number", "Product Name", "UUID", "Wake-up Type"]
    raw_data = {}

    for key in filter_keys:
        try:
            res = subprocess.Popen("sudo dmidecode -t system|grep '%s'" % key, stdout=subprocess.PIPE, shell=True)
            result = res.stdout.read().decode()
            data_list = result.split(':')

            if len(data_list) > 1:
                raw_data[key] = data_list[1].strip()
            else:
                raw_data[key] = ''
        except Exception as e:
            print(e)
            raw_data[key] = ''

    data = dict()
    data["asset_type"] = "server"
    data["manufacturer"] = raw_data["Manufacturer"]
    data["sn"] = raw_data["Serial Number"]
    data["model"] = raw_data["Product Name"]
    data["uuid"] = raw_data["UUID"]
    data["wake_up_type"] = raw_data["Wake-up Type"]

    data.update(get_os_info())
    data.update(get_cpu_info())
    data.update(get_ram_info())
    data.update(get_nic_info())
    data.update(get_disk_info())
    return data

def get_os_info():
    """
    获取操作系统信息
    :return:
    """

    release = subprocess.Popen("sw_vers -a|grep 'ProductVersion'", stdout=subprocess.PIPE, shell=True)
    release = release.stdout.read().decode().split(":")
    data_dic = {
        "os_distribution": "APPLE",
        "os_release": release[1].strip() if len(release) > 1 else "",
        "os_type": "Mac OS X",
    }

    return data_dic

def get_cpu_info():
    """
    获取CPU信息
    :return:
    """
    raw_cmd = "sysctl machdep.cpu"

    raw_data = {
        'cpu_model': "%s |grep 'machdep.cpu.brand_string'|head -1 " % raw_cmd,
        'cpu_core_count': "%s |grep 'machdep.cpu.core_count'" % raw_cmd,
    }

    for key, cmd in raw_data.items():
        try:
            result = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            raw_data[key] = result.stdout.read().decode().strip()
        except ValueError as e:
            print(e)
            raw_data[key] = ""

    data = {
        "cpu_model": raw_data["cpu_model"],
        "cpu_count": 1,
        "cpu_core_count": raw_data["cpu_core_count"],
    }

    cpu_model = raw_data["cpu_model"].split(":")
    data["cpu_model"] = cpu_model[1].strip()

    cpu_core_count = raw_data["cpu_core_count"].split(":")
    data["cpu_core_count"] = int(cpu_core_count[1].strip())

    return data

def get_ram_info():
    """
    获取内存信息
    :return:
    """
    raw_data = subprocess.Popen("dmidecode -t memory", stdout=subprocess.PIPE, shell=True)
    raw_list = raw_data.stdout.read().decode().split("\n")
    raw_ram_list = []
    item_list = []

    """
    raw_list = ['# dmidecode 3.1', 'Getting SMBIOS data from Apple SMBIOS service.', 'SMBIOS 3.0 present.', '',
     'Handle 0x0000, DMI type 16, 23 bytes', 'Physical Memory Array', '\tLocation: System Board Or Motherboard',
     '\tUse: System Memory', '\tError Correction Type: None', '\tMaximum Capacity: 16 GB',
     '\tError Information Handle: Not Provided', '\tNumber Of Devices: 2', '', 'Handle 0x0001, DMI type 17, 84 bytes',
     'Memory Device', '\tArray Handle: 0x0000', '\tError Information Handle: Not Provided', '\tTotal Width: 64 bits',
     '\tData Width: 64 bits', '\tSize: 8192 MB', '\tForm Factor: Row Of Chips', '\tSet: None',
     '\tLocator: ChannelA-DIMM0', '\tBank Locator: BANK 0', '\tType: LPDDR3', '\tType Detail: Synchronous',
     '\tSpeed: 2133 MT/s', '\tManufacturer: Samsung', '\tSerial Number: 55000000', '\tAsset Tag: 9876543210',
     '\tPart Number: K4EBE304EC-EGCG   ', '\tRank: 2', '\tConfigured Clock Speed: 2133 MT/s',
     '\tMinimum Voltage: Unknown', '\tMaximum Voltage: Unknown', '\tConfigured Voltage: 1.2 V', '',
     'Handle 0x0002, DMI type 17, 84 bytes', 'Memory Device', '\tArray Handle: 0x0000',
     '\tError Information Handle: Not Provided', '\tTotal Width: 64 bits', '\tData Width: 64 bits', '\tSize: 8192 MB',
     '\tForm Factor: Row Of Chips', '\tSet: None', '\tLocator: ChannelB-DIMM0', '\tBank Locator: BANK 2',
     '\tType: LPDDR3', '\tType Detail: Synchronous', '\tSpeed: 2133 MT/s', '\tManufacturer: Samsung',
     '\tSerial Number: 55000000', '\tAsset Tag: 9876543210', '\tPart Number: K4EBE304EC-EGCG   ', '\tRank: 2',
     '\tConfigured Clock Speed: 2133 MT/s', '\tMinimum Voltage: Unknown', '\tMaximum Voltage: Unknown',
     '\tConfigured Voltage: 1.2 V', '', '']
    """

    for line in raw_list:
        if line.startswith("Memory Device"):
            raw_ram_list.append(item_list)
            item_list = []
        else:
            item_list.append(line.strip())
    raw_ram_list.append(item_list)

    ram_list = []
    for item in raw_ram_list:
        item_ram_size = 0
        ram_item_to_dic = {}
        for i in item:
            data = i.split(":")
            if len(data) == 2:
                key, v = data
                if key == 'Size':
                    if v.strip() != "No Module Installed":
                        ram_item_to_dic['capacity'] = v.split()[0].strip()
                        item_ram_size = round(float(v.strip()[0]))
                    else:
                        ram_item_to_dic['capacity'] = 0

                if key == 'Type':
                    ram_item_to_dic['model'] = v.strip()
                if key == "Manufacturer":
                    ram_item_to_dic['manufacturer'] = v.strip()
                if key == 'Serial Number':
                    ram_item_to_dic['sn'] = v.strip()
                if key == 'Asset Tag':
                    ram_item_to_dic['asset_tag'] = v.strip()
                if key == 'Locator':
                    ram_item_to_dic['slot'] = v.strip()

        if item_ram_size == 0:
            pass
        else:
            ram_list.append(ram_item_to_dic)

    ram_data = {'ram': ram_list}
    total_gb_size = subprocess.Popen("top -l 1 | head -n 10 | grep PhysMem", stdout=subprocess.PIPE, shell=True)
    total_gb_size = total_gb_size.stdout.read().decode().split(":")[1].split()[0].strip("G")
    ram_data['ram_size'] = total_gb_size

    return ram_data

def get_nic_info():
    """
    获取网卡信息
    :return:
    """
    raw_data = subprocess.Popen("ifconfig -a", stdout=subprocess.PIPE, shell=True)
    raw_data = raw_data.stdout.read().decode().split("\n")

    nic_dic = dict()
    next_ip_line = False
    last_mac_addr = None

    for line in raw_data:
        if next_ip_line:
            next_ip_line = False
            nic_name = last_mac_addr.split()[0]
            mac_addr = last_mac_addr.split("HWaddr")[1].strip()
            raw_ip_addr = line.split("inet addr:")
            raw_bcast = line.split("Bcast:")
            raw_netmask = line.split("Mask:")

            if len(raw_ip_addr) > 1:
                ip_addr = raw_ip_addr[1].split()[0]
                network = raw_bcast[1].split()[0]
                netmask = raw_netmask[1].split()[0]
            else:
                ip_addr = None
                network = None
                netmask = None

            if mac_addr not in nic_dic:
                nic_dic[mac_addr] = {
                                    'name': nic_name,
                                    'mac': mac_addr,
                                    'net_mask': netmask,
                                    'network': network,
                                    'bonding': 0,
                                    'model': 'unknown',
                                    'ip_address': ip_addr,
                                    }
            else:
                if '%s_bonding_addr' % (mac_addr,) not in nic_dic:
                    random_mac_addr = '%s_bonding_addr' % (mac_addr,)
                else:
                    random_mac_addr = '%s_bonding_addr2' % (mac_addr,)

                nic_dic[random_mac_addr] = {
                                            'name': nic_name,
                                            'mac': random_mac_addr,
                                            'net_mask': netmask,
                                            'network': network,
                                            'bonding': 1,
                                            'model': 'unknown',
                                            'ip_address': ip_addr,
                                            }

        if "HWaddr" in line:
            next_ip_line = True
            last_mac_addr = line

    nic_list = []
    for k, v in nic_dic.items():
        nic_list.append(v)

    return {'nic': nic_list}

def get_disk_info():
    """
    获取存储信息。
    本脚本只针对ubuntu中使用sda，且只有一块硬盘的情况。
    具体查看硬盘信息的命令，请根据实际情况，实际调整。
    如果需要查看Raid信息，可以尝试MegaCli工具。
    :return:
    """
    try:
        raw_data = subprocess.Popen("diskutil info disk1", stdout=subprocess.PIPE, shell=True)
        raw_list = raw_data.stdout.read().decode().split("\n")


        disk_list = []
        disk_item_to_dict = {}
        for line in raw_list:
            line = line.strip()
            if line.startswith("Device / Media Name"):
                disk_item_to_dict["model"] = line.split(":")[1].strip()
            elif line.startswith("Disk / Partition UUID"):
                disk_item_to_dict["sn"] = line.split(":")[1].strip()
            elif line.startswith("Disk Size"):
                disk_item_to_dict["size"] = line.split()[2]

        result = {'physical_disk_driver': []}
        result["physical_disk_driver"].append(disk_item_to_dict)
    except:
        result = {'physical_disk_driver': []}
        print("命令错误，跳过磁盘检查")

    return result


if __name__ == "__main__":
    # 收集信息功能测试
    data = collect()
    print(data)

