import json
from assets import models
from utils.utils import date_checker


def log(log_type, msg=None, asset=None, new_asset=None, request=None):
    """  记录日志  """
    event = models.EventLog()
    if log_type == "upline":
        event.name = "%s <%s>:  上线" % (asset.name, asset.sn)
        event.asset = asset
        event.detail = "资产成功上线！"
        event.user = request.user
    elif log_type == "create_succeeded":
        event.name = "%s <%s>:  已创建" % (asset.name, asset.sn)
        event.asset = asset
        event.detail = "资产成功录入！"
    elif log_type == "create_failed":
        event.name = "%s <%s>:  创建失败" % (asset.name, asset.sn)
        event.asset = asset
        event.detail = "资产录入失败！ \n%s" % msg
    elif log_type == "approve_succeeded":
        event.name = "%s <%s>:  审批通过" % (asset.asset_type, asset.sn)
        event.asset = asset
        event.detail = "审批通过！"
        event.user = request.user
    elif log_type == "approve_failed":
        event.name = "%s <%s>:  审批失败" % (new_asset.asset_type, new_asset.sn)
        event.new_asset = new_asset
        event.detail = "审批失败！\n%s" % msg
        event.user = request.user
    elif log_type == "update_succeeded":
        event.name = "%s <%s>: 数据更新！" % (asset.asset_type, asset.sn)
        event.asset = asset
        event.detail = "更新成功！"
    elif log_type == "update_failed":
        event.name = "%s <%s>: 更新失败" % (asset.asset_type, asset.sn)
        event.asset = asset
        event.detail = "更新失败！ \n%s" % msg
    # 更多日志类型......
    event.save()

class NewAsset(object):
    def __init__(self, request, data):
        self.request = request
        self.data = data

        self.asset_type = self.data.get('asset_type')

        self.sn = self.data.get('sn')
        self.model = self.data.get('model')
        self.created_by = self.data.get('created_by')
        # 服务器
        self.raid_type = self.data.get('raid_type')
        self.cpu_model = self.data.get('cpu_model')
        self.cpu_count = self.data.get('cpu_count')
        self.cpu_core_count = self.data.get('cpu_core_count')
        self.os_type = self.data.get('os_type')
        self.os_distribution = self.data.get('os_distribution')
        self.os_release = self.data.get('os_release')
        # 安全设备
        self.sub_asset_type = self.data.get('sub_asset_type')
        # 存储设备

        # 网络设备
        self.vlan_ip = self.data.get('vlan_ip')
        self.intranet_ip = self.data.get('intranet_ip')
        self.firmware = self.data.get('firmware')
        self.port_num = self.data.get('port_num')
        self.device_detail = self.data.get('device_detail')
        # 软件/系统
        self.license_num = self.data.get('license_num')
        self.version = self.data.get('version')

    ## # 新资产录入/上报 调用方法
    ## def add_to_new_assets_zone(self):
    ##     defaults = {
    ##         'data': json.dumps(self.data),
    ##         'asset_type': self.data.get('asset_type'),
    ##         'manufacturer': self.data.get('manufacturer'),
    ##         'model': self.data.get('model'),
    ##         'ram_size': self.data.get('ram_size'),
    ##         'cpu_model': self.data.get('cpu_model'),
    ##         'cpu_count': self.data.get('cpu_count'),
    ##         'cpu_core_count': self.data.get('cpu_core_count'),
    ##         'os_distribution': self.data.get('os_distribution'),
    ##         'os_release': self.data.get('os_release'),
    ##         'os_type': self.data.get('os_type'),
    ##     }
    ##     try:
    ##         self.asset_upline_pre()
    ##         # models.NewAssetApprovalZone.objects.update_or_create(sn=self.data['sn'], defaults=defaults)
    ##         models.NewAssetApprovalZone.objects.update_or_create(approved=False, defaults=defaults)
    ##     except Exception as e:
    ##         log('asset_create_failed', msg=e, new_asset=self.data, request=self.request)
    ##         return False
    ##     else:
    ##         return "资产已经加入或更新待审批区！"


    # 各类资产写入的入口方法
    # def asset_upline_pre(self):
    def add_to_new_assets_zone(self):
        # 为以后的其他类型资产扩展预留接口
        # func = getattr(self, "_%s_upline" % self.new_asset.asset_type)
        func = getattr(self, "_%s_upline_pre" % self.data.get('asset_type'))
        ret = func()
        return ret

    def _create_new_asset_approval_zone(self, asset):
        defaults = {
            'data': json.dumps(self.data),
            # 'asset_type': self.data.get('asset_type'),
            # 'manufacturer': self.data.get('manufacturer'),
            # 'model': self.data.get('model'),
            # 'ram_size': self.data.get('ram_size'),
            # 'cpu_model': self.data.get('cpu_model'),
            # 'cpu_count': self.data.get('cpu_count'),
            # 'cpu_core_count': self.data.get('cpu_core_count'),
            # 'os_distribution': self.data.get('os_distribution'),
            # 'os_release': self.data.get('os_release'),
            # 'os_type': self.data.get('os_type'),
        }
        models.NewAssetApprovalZone.objects.update_or_create(asset=asset, approved=False, defaults=defaults)

    # 服务器写入方法
    def _server_upline_pre(self):
        # 在实际的生产环境中，下面的操作应该是原子性的整体事务，任何一步出现异常，所有操作都要回滚。
        asset = self._create_asset()   # 创建一条资产并返回资产对象。注意要和待审批区的资产区分开。
        try:
            self._create_manufacturer(asset)  # 创建厂商
            self._create_server(asset)        # 创建服务器
            self._create_CPU(asset)           # 创建CPU
            self._create_RAM(asset)           # 创建内存
            self._create_disk(asset)          # 创建硬盘
            self._create_nic(asset)           # 创建网卡
            self._create_new_asset_approval_zone(asset)   # 创建待审批表记录
            # self._delete_original_asset()     # 从待审批资产区删除已经审批上线的资产
        except Exception as e:
            asset.delete()
            # log('approve_failed', msg=e, new_asset=self.new_asset, request=self.request)
            log('create_failed', msg=e, new_asset=self.data, request=self.request)
            print(e)
            return False
        else:
            # 创建成功，添加日志
            log("create_succeeded", asset=asset, request=self.request)
            print("新服务器上线！")
            return True
    def _networkdevice_upline_pre(self):
        asset = self._create_asset()
        try:
            self._create_manufacturer(asset)
            self._create_networkdevice(asset)
            self._create_new_asset_approval_zone(asset)   # 创建待审批表记录
        except Exception as e:
            asset.delete()
            log('create_failed', msg=e, new_asset=self.data, request=self.request)
            print(e)
            return False
        else:
            # 创建成功，添加日志
            log("create_succeeded", asset=asset, request=self.request)
            print("新网络设备上线！")
            return True

    def _storagedevice_upline_pre(self):
        asset = self._create_asset()
        try:
            self._create_manufacturer(asset)
            self._create_storagedevice(asset)
            self._create_new_asset_approval_zone(asset)  # 创建待审批表记录
        except Exception as e:
            asset.delete()
            log('create_failed', msg=e, new_asset=self.data, request=self.request)
            print(e)
            return False
        else:
            # 创建成功，添加日志
            log("create_succeeded", asset=asset, request=self.request)
            print("新存储设备上线！")
            return True
    def _securitydevice_upline_pre(self):
        asset = self._create_asset()
        try:
            self._create_manufacturer(asset)
            self._create_securitydevice(asset)
            self._create_new_asset_approval_zone(asset)  # 创建待审批表记录
        except Exception as e:
            asset.delete()
            log('create_failed', msg=e, new_asset=self.data, request=self.request)
            print(e)
            return False
        else:
            # 创建成功，添加日志
            log("create_succeeded", asset=asset, request=self.request)
            print("新安全设备上线！")
            return True
    def _software_upline_pre(self):
        asset = self._create_asset()
        try:
            self._create_manufacturer(asset)
            self._create_software(asset)
            self._create_new_asset_approval_zone(asset)  # 创建待审批表记录
        except Exception as e:
            asset.delete()
            log('create_failed', msg=e, new_asset=self.data, request=self.request)
            print(e)
            return False
        else:
            # 创建成功，添加日志
            log("create_succeeded", asset=asset, request=self.request)
            print("新软件/系统上线！")
            return True

    def _create_asset(self):
        """
        创建资产并上线
        :return:
        """
        # 利用request.user自动获取当前管理人员的信息，作为审批人添加到资产数据中。
        # asset = models.Asset.objects.create(asset_type=self.new_asset.asset_type, name="%s: %s" % (self.new_asset.asset_type, self.new_asset.sn), sn=self.new_asset.sn, approved_by=self.request.user)
        asset = models.Asset.objects.create(asset_type=self.asset_type, name="%s: %s" % (self.asset_type, self.sn), sn=self.sn, status=0)
        return asset

    def _create_manufacturer(self, asset):
        """
        创建厂商
        :param asset:
        :return:
        """
        # 判断厂商数据是否存在。如果存在，看看数据库里是否已经有该厂商，再决定是获取还是创建。
        # m = self.new_asset.manufacturer
        m = self.data.get('manufacturer')
        if m:
            manufacturer_obj, _ = models.Manufacturer.objects.get_or_create(name=m)
            asset.manufacturer = manufacturer_obj
            asset.save()

    def _create_server(self, asset):
        """
        创建服务器
        :param asset:
        :return:
        """
        # models.Server.objects.create(asset=asset, model=self.new_asset.model, os_type=self.new_asset.os_type, os_distribution=self.new_asset.os_distribution, os_release=self.new_asset.os_release,)
        models.Server.objects.create(
            asset=asset,
            sub_asset_type=self.sub_asset_type,
            # created_by=
            # hosted_on=
            model=self.model,
            raid_type=self.raid_type,
            os_type=self.os_type,
            os_distribution=self.os_distribution,
            os_release=self.os_release,
        )

    def _create_networkdevice(self, asset):
        """ 创建网络设备"""
        models.NetworkDevice.objects.create(
            asset=asset,
            sub_asset_type=self.sub_asset_type,
            vlan_ip=self.vlan_ip,
            intranet_ip=self.intranet_ip,
            firmware=self.firmware,
            port_num=self.port_num,
            device_detail=self.device_detail,
        )
    def _create_storagedevice(self, asset):
        """ 创建存储设备"""
        models.StorageDevice.objects.create(asset=asset, sub_asset_type=self.sub_asset_type,)

    def _create_securitydevice(self, asset):
        """ 创建安全设备 """
        models.SecurityDevice.objects.create(asset=asset, sub_asset_type=self.sub_asset_type,)

    def _create_software(self, asset):
        """ 创建软件/系统 """
        models.Software.objects.create(
            asset=asset,
            sub_asset_type=self.sub_asset_type,
            license_num=self.license_num,
            version=self.version,
        )

    def _create_CPU(self, asset):
        """
        创建CPU.
        教程这里对发送过来的数据采取了最大限度的容忍，
        实际情况下你可能还要对数据的完整性、合法性、数据类型进行检测，
        根据不同的检测情况，是被动接收，还是打回去要求重新收集，请自行决定。
        这里的业务逻辑非常复杂，不可能面面俱到。
        :param asset:
        :return:
        """
        cpu = models.CPU.objects.create(asset=asset)
        # cpu.cpu_model = self.new_asset.cpu_model
        # cpu.cpu_count = self.new_asset.cpu_count
        # cpu.cpu_core_count = self.new_asset.cpu_core_count
        cpu.cpu_model = self.cpu_model
        cpu.cpu_count = self.cpu_count
        cpu.cpu_core_count = self.cpu_core_count
        cpu.save()

    def _create_RAM(self, asset):
        """
        创建内存。通常有多条内存
        :param asset:
        :return:
        """
        ram_list = self.data.get('ram')
        if not ram_list:    # 万一一条内存数据都没有
            return
        for ram_dict in ram_list:
            if not ram_dict.get('slot'):
                raise ValueError("未知的内存插槽！")  # 使用虚拟机的时候，可能无法获取内存插槽，需要你修改此处的逻辑。
            ram = models.RAM()
            ram.asset = asset
            ram.slot = ram_dict.get('slot')
            ram.sn = ram_dict.get('sn')
            ram.model = ram_dict.get('model')
            ram.manufacturer = ram_dict.get('manufacturer')
            ram.capacity = ram_dict.get('capacity', 0)
            ram.save()

    def _create_disk(self, asset):
        """
        存储设备种类多，还有Raid情况，需要根据实际情况具体解决。
        这里只以简单的SATA硬盘为例子。可能有多块硬盘。
        :param asset:
        :return:
        """
        disk_list = self.data.get('physical_disk_driver')
        if not disk_list:   # 一条硬盘数据都没有
            return
        for disk_dict in disk_list:
            if not disk_dict.get('sn'):
                raise ValueError("未知SN 的硬盘！")  # 根据sn确定具体某块硬盘。
            disk = models.Disk()
            disk.asset = asset
            disk.sn = disk_dict.get('sn')
            disk.model = disk_dict.get('model')
            disk.manufacturer = disk_dict.get('manufacturer')
            disk.slot = disk_dict.get('slot')
            disk.capacity = disk_dict.get('capacity', 0)
            interface = disk_dict.get('interface_type')
            if interface in ['SATA', 'SAS', 'SCSI', 'SSD', 'unknown']:
                disk.interface_type = interface

            disk.save()

    def _create_nic(self, asset):
        """
        创建网卡。可能有多个网卡，甚至虚拟网卡。
        :param asset:
        :return:
        """
        nic_list = self.data.get("nic")
        if not nic_list:
            return

        for nic_dict in nic_list:
            if not nic_dict.get('mac'):
                raise ValueError("网卡缺少MAC地址！")
            if not nic_dict.get("model"):
                raise ValueError("网卡型号未知！")

            nic = models.NIC()
            nic.asset = asset
            nic.name = nic_dict.get('name')
            nic.model = nic_dict.get('model')
            nic.mac = nic_dict.get('mac')
            nic.ip_address = nic_dict.get('ip_address')
            if nic_dict.get('net_mask'):
                if len(nic_dict.get('net_mask')) > 0:
                    nic.net_mask = nic_dict.get('net_mask')[0]

            nic.save()


# 资产审核
class ApproveAsset:
    """  审批资产并上线。  """
    def __init__(self, request, asset_id):
        self.request = request
        self.new_asset = models.NewAssetApprovalZone.objects.get(id=asset_id)
        # print("NEW_ASSET" ,self.new_asset)
        self.data = json.loads(self.new_asset.data)



    def _delete_original_asset(self):
        """
        这里的逻辑是已经审批上线的资产，就从待审批区删除。
        也可以设置为修改成已审批状态但不删除，只是在管理界面特别处理，不让再次审批，灰色显示。
        不过这样可能导致待审批区越来越大。
        :return:
        """
        self.new_asset.delete()

class UpdateAsset:
    """
    1. 自动更新已上线的资产；
    2. 手动更新；
    如果想让记录的日志更详细，可以逐条对比数据项，将更新过的项目记录到log信息中。
    """
    def __init__(self, request, asset, data):
        self.request = request
        self.asset = asset
        self.data = data    # 此处的数据是由客户端发送过来的整个数据字符串
        # self.asset_update()

    def asset_update(self):
        # 为以后的其它类型资产扩展留下接口
        func = getattr(self, "_%s_update" % self.asset.asset_type)
        ret = func()
        return ret

    def _update_asset(self):
        """ 更新资产公共信息 """
        # self.asset_type = self.data.get('asset_type')
        self.asset.sn = self.data.get('sn')
        self.asset.status = self.data.get("status")
        self.asset.asset_level = self.data.get("asset_level")
        self.asset.manage_ip = self.data.get("manage_ip")
        ##### self.asset.admin = self.data.get("admin")
        self.asset.price = self.data.get("price")
        ##### self.asset.approved_by = self.data.get("approved_by")
        self.asset.created_by = self.data.get("created_by")
        self.asset.remark = self.data.get("remark")

        # 处理日期格式
        self.asset.purchase_day = date_checker(self.data.get("purchase_day"))
        self.asset.expire_day = date_checker(self.data.get("expire_day"))
        # 业务线
        business_unit = self.data.get("business_unit")
        self.asset.business_unit = models.BusinessUnit.objects.get(pk=business_unit)
        # 机房
        idc = self.data.get("idc")
        if idc:
            self.asset.idc = models.IDC.objects.get(pk=idc)
        # 厂商
        manufacturer = self.data.get("manufacturer")
        if manufacturer:
            self.asset.manufacturer = models.Manufacturer.objects.get(name=manufacturer)
        # 合同
        contract = self.data.get("contract")
        if contract:
            self.asset.contract = models.Contract.objects.get(pk=contract)
        # 标签
        tags = self.data.get("tags")
        if tags:
            for tag in tags:
                tag = models.Tag.objects.get(pk=tag)
                self.asset.tags.add(tag)
        # self.asset.asset.save()    # _server_update 中需要再次执行 save()，因此这里不需要 save()


    def _update_manufacturer(self):
        """
        更新厂商
        """
        m = self.data.get("manufacturer")
        if m:
            manufacturer_obj, _ = models.Manufacturer.objects.get_or_create(name=m)
            self.asset.manufacturer = manufacturer_obj
        else:
            self.asset.manufacturer = None
        self.asset.manufacturer.save()

    def _server_update(self):
        try:
            self._update_manufacturer()
            self._update_server()
            self._update_CPU()
            self._update_RAM()
            self._update_disk()
            self._update_nic()
            self._update_asset()
            self.asset.save()
        except Exception as e:
            log("update_failed", msg=e, asset=self.asset, request=self.request)
            print(e)
            return False
        else:
            # 添加日志
            log("update_succeeded", asset=self.asset)
            print("资产数据被更新")
            return True

    def _update_server(self):
        """
        更新服务器
        """
        self.asset.server.sub_asset_type = self.data.get("sub_asset_type")
        self.asset.server.created_by = self.data.get("created_by")
        self.asset.server.model = self.data.get("model")
        self.asset.server.raid_type = self.data.get("raid_type")
        self.asset.server.os_type = self.data.get("os_type")
        self.asset.server.os_distribution = self.data.get("os_distribution")
        self.asset.server.os_release = self.data.get("os_release")
        self.asset.server.remark = self.data.get("remark")
        # 处理 hosted_on宿主机
        hosted_on = self.data.get("hosted_on")
        if hosted_on:
            try:
                hosted_on = models.Server.objects.get(pk=hosted_on)
                self.asset.server.hosted_on = hosted_on
            except:
                pass
        self.asset.server.save()

    def _update_CPU(self):
        """
        更新CPU信息
        :return:
        """
        self.asset.cpu.cpu_model = self.data.get("cpu_Model")
        self.asset.cpu.cpu_count = self.data.get("cpu_count")
        self.asset.cpu.cpu_core_count = self.data.get("cpu_core_count")
        self.asset.cpu.save()

    def _update_RAM(self):
        """
        更新内存信息。
        使用集合数据类型中差的概念，处理不同的情况。
        如果新数据有，但原数据没有，则新增；
        如果新数据没有，但原数据有，则删除原来多余的部分；
        如果新的和原数据都有，则更新。
        在原则上，下面的代码应该写成一个复用的函数，
        但是由于内存、硬盘、网卡在某些方面的差别，导致很难提取出重用的代码。
        :return:
        """
        # 获取已有内存信息，并转成字典格式
        old_rams = models.RAM.objects.filter(asset=self.asset)
        old_rams_dict = dict()
        if old_rams:
            for ram in old_rams:
               old_rams_dict[ram.slot] = ram
        # 获取新数据中的内存信息，并转成字典格式
        new_rams_list = self.data["ram"]
        new_rams_dict = dict()
        if new_rams_list:
            for item in new_rams_list:
                new_rams_dict[item["slot"]] = item
        # 利用set类型的差集功能，获得需要删除的内存数据对象
        need_deleted_keys = set(old_rams_dict.keys()) - set(new_rams_dict.keys())
        if need_deleted_keys:
            for key in need_deleted_keys:
                old_rams_dict[key].delete()

        # 需要新增或更新的
        if new_rams_dict:
            for key in new_rams_dict:
                defaults = {
                    "sn": new_rams_dict[key].get("sn"),
                    "model": new_rams_dict[key].get("model"),
                    "manufacturer": new_rams_dict[key].get("manufacturer"),
                    "capacity": new_rams_dict[key].get("capacity", 0),
                }
                models.RAM.objects.update_or_create(asset=self.asset, slot=key, defaults=defaults)

    def _update_disk(self):
        """
        更新硬盘信息。类似更新内存。
        """
        old_disks = models.Disk.objects.filter(asset=self.asset)
        old_disks_dict = dict()
        if old_disks:
            for disk in old_disks:
                old_disks_dict[disk.sn] = disk

        new_disks_list = self.data["physical_disk_dirver"]
        new_disks_dict = dict()

        if new_disks_list:
            for item in new_disks_list:
                new_disks_dict[item["sn"]] = item

        # 需要删除的
        need_deleted_keys = set(old_disks_dict.keys()) - set(new_disks_dict.keys())
        if need_deleted_keys:
            for key in need_deleted_keys:
                old_disks_dict[key].delete()
        # 需要新增或更新的
        if new_disks_dict:
            for key in new_disks_dict:
                interface_type = new_disks_dict[key].get("interface_type", "unknown")
                if interface_type not in ["SATA", "SAS", "SCSI", "SSD", "unknown"]:
                    interface_type = "unknown"
                defaults = {
                    "slot": new_disks_dict[key].get("slot"),
                    "model": new_disks_dict[key].get("models"),
                    "manufacturer": new_disks_dict[key].get("manufacturer"),
                    "capacity": new_disks_dict[key].get("capacity", 0),
                    "interface_type": interface_type,
                }
                models.Disk.objects.update_or_create(asset=self.asset, sn=key, defaults=defaults)

    def _update_nic(self):
        """
        更新网卡信息。类似更新内存。
        """
        old_nics = models.NIC.objects.filter(asset=self.asset)
        old_nics_dict = dict()
        if old_nics:
            for nic in old_nics:
                old_nics_dict[nic.model+nic.mac] = nic

        new_nics_list = self.data["nic"]
        new_nics_dict = dict()
        if new_nics_list:
            for item in new_nics_list:
                new_nics_dict[item["model"]+item["mac"]] = item

        # 需要删除的
        need_deleted_keys = set(old_nics_dict.keys()) - set(new_nics_dict.keys())
        if need_deleted_keys:
            for key in need_deleted_keys:
                old_nics_dict[key].delete()
        # 需要新增或更新的
        if new_nics_dict:
            for key in new_nics_dict:
                if new_nics_dict[key].get("net_mask") and len(new_nics_dict[key].get("net_mask")) > 0:
                    net_mask = new_nics_dict[key].get("net_mask")[0]
                else:
                    net_mask = ""

                defaults = {
                    "name": new_nics_dict[key].get("name"),
                    "ip_address": new_nics_dict[key].get("ip_address"),
                    "net_mask": net_mask,
                }
                models.NIC.objects.update_or_create(asset=self.asset, model=new_nics_dict[key]["model"], mac=new_nics_dict[key]["mac"], defaults=defaults)

        print("更新成功！")

    # 更新安全设备
    def _securitydevice_update(self):
        try:
            self._update_asset()
            self._update_manufacturer()
            self._update_securitydevice()
            self.asset.save()
        except Exception as e:
            log("update_failed", msg=e, asset=self.asset, request=self.request)
            print(e)
            return False
        else:
            # 添加日志
            log("update_succeeded", asset=self.asset)
            print("安全设备被更新")
            return True

    def _update_securitydevice(self):
        self.asset.securitydevice.sub_asset_type = self.data.get('sub_asset_type')
        self.asset.securitydevice.model = self.data.get('model')
        self.asset.securitydevice.save()

    # 更新存储设备
    def _storagedevice_update(self):
        try:
            self._update_asset()
            self._update_manufacturer()
            self._update_storagedevice()
            self.asset.save()
        except Exception as e:
            log("update_failed", msg=e, asset=self.asset, request=self.request)
            print(e)
            return False
        else:
            # 添加日志
            log("update_succeeded", asset=self.asset)
            print("资产数据被更新")
            return True

    def _update_storagedevice(self):
        self.asset.storagedevice.sub_asset_type = self.data.get('sub_asset_type')
        self.asset.storagedevice.model = self.data.get('model')
        self.asset.storagedevice.save()

    # 更新网络设备
    def _networkdevice_update(self):
        try:
            self._update_asset()
            self._update_manufacturer()
            self._update_networkdevice()
            self.asset.save()
        except Exception as e:
            log("update_failed", msg=e, asset=self.asset, request=self.request)
            print(e)
            return False
        else:
            # 添加日志
            log("update_succeeded", asset=self.asset)
            print("资产数据被更新")
            return True

    def _update_networkdevice(self):
        self.asset.networkdevice.sub_asset_type = self.data.get('sub_asset_type')
        self.asset.networkdevice.vlan_ip = self.data.get('vlan_ip')
        self.asset.networkdevice.intranet_ip = self.data.get('intranet_ip')
        self.asset.networkdevice.model = self.data.get('model')
        self.asset.networkdevice.firmware = self.data.get('firmware')
        self.asset.networkdevice.port_num = self.data.get('port_num')
        self.asset.networkdevice.device_detail = self.data.get('device_detail')
        self.asset.networkdevice.save()

    # 更新软件
    def _software_update(self):
        try:
            self._update_asset()
            self._update_manufacturer()
            self._update_software()
            self.asset.save()
        except Exception as e:
            log("update_failed", msg=e, asset=self.asset, request=self.request)
            print(e)
            return False
        else:
            # 添加日志
            log("update_succeeded", asset=self.asset)
            print("资产数据被更新")
            return True

    def _software_update(self):
        self.asset.software.sub_asset_type = self.data.get('sub_asset_type')
        self.asset.software.license_num = self.data.get('license_num')
        self.asset.software.version = self.data.get('version')
        self.asset.software.save()
