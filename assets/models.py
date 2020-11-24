from django.db import models

from utils.basemodels import Basemodel

# from django.contrib.auth.models import User
from accounts.models import Users

# Create your models here.


class Asset(Basemodel):
    """  所有资产的共有数据表  """
    asset_type_choice = (
        ('server', '服务器'),
        ('networkdevice', '网络设备'),
        ('storagedevice', '存储设备'),
        ('securitydevice', '安全设备'),
        ('software', '软件资产'),
    )
    asset_status = (
        # 待审批;备用;预上线;在线;故障;下线;未知;
        (0, "待审批"),
        (1, '在线'),
        (2, '下线'),
        (3, '未知'),
        (4, '故障'),
        (5, '备用'),
        (6, '待分配'),
        (7, '已删除'),

    )
    asset_level_choice = (
        (1, "生产环境"),
        (2, "准生产环境"),
        (3, "测试环境"),
        (4, "开发环境"),
    )
    created_by_choice = (
        ("auto", "自动添加"),
        ("manual", "手工录入"),
    )

    asset_type = models.CharField(choices=asset_type_choice, max_length=64, default='server', verbose_name='资产类型')
    name = models.CharField(default='', max_length=64, unique=True, verbose_name="资产名称")  # 唯一
    sn = models.CharField(max_length=128, unique=True, verbose_name="资产序列号") # 唯一
    business_unit = models.ForeignKey('BusinessUnit', null=True, blank=True, verbose_name="所属业务线", on_delete=models.SET_NULL)
    status = models.SmallIntegerField(choices=asset_status, default=0, verbose_name="设备状态(待审批;备用;预上线;在线;故障;下线;未知;)")
    asset_level = models.SmallIntegerField(choices=asset_level_choice, null=True, verbose_name="资产所属业务等级")

    manufacturer = models.ForeignKey('Manufacturer', null=True, blank=True, verbose_name="制造商", on_delete=models.SET_NULL)
    manage_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="管理IP")
    tags = models.ManyToManyField('Tag', blank=True, verbose_name="标签")
    admin = models.ForeignKey(Users, null=True, blank=True, verbose_name="资产管理员", related_name='admin', on_delete=models.SET_NULL)
    idc = models.ForeignKey('IDC', null=True, blank=True, verbose_name="所在机房", on_delete=models.SET_NULL)
    contract = models.ForeignKey('Contract', null=True, blank=True, verbose_name="合同", on_delete=models.SET_NULL)

    purchase_day = models.DateField(null=True, blank=True, verbose_name="购买日期")
    expire_day = models.DateField(null=True, blank=True, verbose_name="过保日期")
    price = models.FloatField(null=True, blank=True, verbose_name="价格")

    approved_by = models.ForeignKey(Users, null=True, verbose_name="审批人", related_name='approved_by', on_delete=models.SET_NULL)
    created_by = models.CharField(choices=created_by_choice, max_length=32, default='auto', verbose_name="添加方式")

    # memo = models.TextField(null=True, blank=True, verbose_name="备注")
    # create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建日期/批准日期")
    # modify_time = models.DateTimeField(auto_now=True, verbose_name="更新日期")

    def __str__(self):
        return '<%s> %s' % (self.get_asset_type_display(), self.name)

    class Meta:
        verbose_name = "资产总表"
        verbose_name_plural = "资产总表"
        ordering = ['-create_time']

class Server(Basemodel):
    """  服务器设备  """
    sub_asset_type_choice = (
        (1, "PC服务器"),
        (2, "刀片机"),
        (3, "小型机"),
    )

    created_by_choice = (
        ("auto", "自动添加"),
        ("manual", "手工录入"),
    )

    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)  # 非常关键的一对一关联！asset被删除的时候一并删除server
    # name = models.CharField(default='', unique=True, blank=True, max_length=128, verbose_name='名称')
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice, default=0, verbose_name="服务器类型")
    created_by = models.CharField(choices=created_by_choice, max_length=32, default='auto', verbose_name="添加方式")
    hosted_on = models.ForeignKey('self', related_name='hosted_on_server', blank=True, null=True, verbose_name="宿主机", on_delete=models.CASCADE)
    model = models.CharField(max_length=128, blank=True, null=True, verbose_name="服务器型号")
    raid_type = models.CharField(max_length=512, blank=True, null=True, verbose_name="Raid类型")

    os_type = models.CharField('操作系统类型', max_length=64, blank=True, null=True)
    os_distribution = models.CharField('发行商', max_length=64, blank=True, null=True)
    os_release = models.CharField('操作系统版本', max_length=64, blank=True, null=True)

    def __str__(self):
        return '%s--%s--%s <sn:%s>' % (self.asset.name, self.get_sub_asset_type_display(), self.model, self.asset.sn)

    class Meta:
        verbose_name = "服务器"
        verbose_name_plural = "服务器"

class SecurityDevice(Basemodel):
    """  安全设备  """
    sub_asset_type_choice = (
        (1, "防火墙"),
        (2, "入侵检测设备"),
        (3, "互联网网关"),
        (4, "运维审计系统"),
    )

    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)
    # name = models.CharField(default='', null=True, blank=True, max_length=128, verbose_name='名称')
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice, default=0, verbose_name="安全设备类型")
    model = models.CharField(max_length=128, default="未知型号", verbose_name="安全设备型号")

    def __str__(self):
        return self.asset.name + "--" + self.get_sub_asset_type_display() + str(self.model) + " id:%s" % self.id

    class Meta:
        verbose_name = "安全设备"
        verbose_name_plural = "安全设备"

class StorageDevice(Basemodel):
    """  存储设备  """
    sub_asset_type_choice = (
        (1, "磁盘阵列"),
        (2, "网络存储器"),
        (3, "磁带库"),
        (4, "磁带机"),
    )

    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice, default=0, verbose_name="存储设备类型")
    model = models.CharField(max_length=128, default="未知型号", verbose_name="存储设备型号")

    def __str__(self):
        return self.asset.name + "--" + self.get_sub_asset_type_display() + str(self.model) + " id:%s" % self.id

    class Meta:
        verbose_name = "存储设备"
        verbose_name_plural = "存储设备"

class NetworkDevice(Basemodel):
    """  网络设备  """
    sub_asset_type_choice = (
        (1, '路由器'),
        (2, "交换机"),
        (3, "负载均衡"),
        (4, "VPN设备"),
    )

    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice, default=0, verbose_name="网络设备类型")

    vlan_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="VLanIP")
    intranet_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="内网IP")

    model = models.CharField(max_length=128, default="未知型号", verbose_name="网络设备型号")
    firmware = models.CharField(max_length=128, blank=True, null=True, verbose_name="设备固件版本")
    port_num = models.SmallIntegerField(null=True, blank=True, verbose_name="端口个数")
    device_detail = models.TextField(null=True, blank=True, verbose_name="详细配置")

    def __str__(self):
        return "%s--%s--%s <sn:%s>" % (self.asset.name, self.get_sub_asset_type_display(), self.model, self.asset.sn)

    class Meta:
        verbose_name = "网络设备"
        verbose_name_plural = "网络设备"

class Software(Basemodel):
    """  软件信息  """
    sub_asset_type_choice = (
        (1, "操作系统"),
        (2, "办公\开发软件"),
        (3, "业务软件"),
    )
    soft_level = (
        (1, "核心生产"),
        (2, "一级生产"),
        (3, "二级生产"),
        (4, "三级生产"),
    )

    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)
    # asset = models.IntegerField(default=0)
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice, default=0, verbose_name="软件类型")
    license_num = models.IntegerField(default=0, verbose_name="授权数量")
    version = models.CharField(max_length=64, unique=True, help_text="例如: RedHat release 7 (Final)", verbose_name="软件/系统版本")

    def __str__(self):
        return "%s--%s" % (self.get_sub_asset_type_display(), self.version)

    class Meta:
        verbose_name = "软件/系统"
        verbose_name_plural = "软件/系统"

class CPU(Basemodel):
    """  CPU组件  """
    asset = models.OneToOneField('Asset', on_delete=models.CASCADE)
    cpu_model = models.CharField(max_length=64, blank=True, null=True, verbose_name="CPU型号")
    cpu_count = models.PositiveIntegerField(default=1, verbose_name="物理CPU个数")
    cpu_core_count = models.PositiveIntegerField(default=1, verbose_name="CPU核心数")

    def __str__(self):
        return self.asset.name + ":  " + self.cpu_model

    class Meta:
        verbose_name = "CPU"
        verbose_name_plural = "CPU"

class RAM(Basemodel):
    """  内存  """
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE)
    sn = models.CharField(max_length=128, blank=True, null=True, verbose_name="SN号")
    model = models.CharField(max_length=128, blank=True, null=True, verbose_name="内存型号")
    manufacturer = models.CharField(max_length=128, blank=True, null=True, verbose_name="内存制造商")
    slot = models.CharField(max_length=64, verbose_name="插槽")
    capacity = models.IntegerField(blank=True, null=True, verbose_name="内存大小(GB)")

    def __str__(self):
        return '%s: %s: %s: %s' % (self.asset.name, self.model, self.slot, self.capacity)

    class Meta:
        verbose_name = "内存"
        verbose_name_plural = "内存"
        unique_together = ("asset", "slot")   # 同一资产下的内存，根据插槽的不同，必须唯一

class Disk(Basemodel):
    """  硬盘  """
    disk_interface_type_choice = (
        ('SATA', 'SATA'),
        ('SAS', 'SAS'),
        ('SCSI', 'SCSI'),
        ('SSD', 'SSD'),
        ('unknown', 'unknown'),
    )

    asset = models.ForeignKey("Asset", on_delete=models.CASCADE)
    sn = models.CharField(max_length=128, verbose_name="硬盘SN码")
    slot = models.CharField(max_length=128, blank=True, null=True, verbose_name="所在插槽位")
    model = models.CharField(max_length=128, blank=True, null=True, verbose_name="磁盘型号")
    manufacturer = models.CharField(max_length=128, blank=True, null=True, verbose_name="磁盘制造商")
    capacity = models.FloatField(blank=True, null=True, verbose_name="磁盘容量(GB)")
    interface_type = models.CharField(max_length=16, choices=disk_interface_type_choice, default="unknown", verbose_name="接口类型")

    def __str__(self):
        return "%s:  %s:  %s:  %sGB" % (self.asset.name, self.model, self.slot, self.capacity)

    class Meta:
        verbose_name = "硬盘"
        verbose_name_plural = "硬盘"
        unique_together = ("asset", "sn")

class NIC(Basemodel):
    """  网卡组件  """
    asset = models.ForeignKey("Asset", on_delete=models.CASCADE)
    model = models.CharField(max_length=64, verbose_name="网卡型号")
    mac = models.CharField(max_length=64, verbose_name="MAC地址")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP地址")
    net_mask = models.CharField(max_length=64, blank=True, null=True, verbose_name="掩码")
    bonding = models.CharField(max_length=64, blank=True, null=True, verbose_name="绑定地址")

    def __str__(self):
        return "%s:  %s:  %s" % (self.asset.name, self.model, self.mac)

    class Meta:
        verbose_name = "网卡"
        verbose_name_plural = "网卡"
        unique_together = ("asset", "model", "mac")

class IDC(Basemodel):
    """  机房  """
    name = models.CharField(default='', unique=True, max_length=128, verbose_name='名称')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "机房"
        verbose_name_plural = "机房"

class Manufacturer(Basemodel):
    """  厂商  """
    name = models.CharField(default='', unique=True, max_length=128, verbose_name='名称')
    telephone = models.CharField(max_length=11, verbose_name="支持电话")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "厂商"
        verbose_name_plural = "厂商"

class BusinessUnit(Basemodel):
    """  业务线  """
    name = models.CharField(default='', unique=True, max_length=128, verbose_name='名称')
    parent_unit = models.ForeignKey('self', blank=True, null=True, related_name="parent_level", on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "业务线"
        verbose_name_plural = "业务线"

class Contract(Basemodel):
    """  合同  """
    sn = models.CharField(max_length=128, unique=True, verbose_name="合同号")
    price = models.IntegerField("合同金额")
    detail = models.TextField(blank=True, null=True, verbose_name="合同明细")
    start_date = models.DateField(blank=True, null=True, verbose_name="开始日期")
    end_date = models.DateField(blank=True, null=True, verbose_name="失效日期")
    license_num =  models.IntegerField(blank=True, null=True, verbose_name="License数量")
    name = models.CharField(default='', unique=True, max_length=128, verbose_name='名称')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "合同"
        verbose_name_plural = "合同"

class Tag(Basemodel):
    """  标签  """
    name = models.CharField(default='', unique=True, max_length=128, verbose_name='名称')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = "标签"

class EventLog(Basemodel):
    """
    日志.
    在关联对象被删除的时候，不能一并删除，需保留日志。
    因此，on_delete=models.SET_NULL
    """
    event_type_choice = (
        (1, "其他"),
        (2, "硬件变更"),
        (3, "新增配件"),
        (4, "设备上线"),
        (5, "设备下线"),
        (6, "定期维护"),
        (7, "业务上线\更新"),
    )

    name = models.CharField(max_length=128,null=True, blank=True, verbose_name="事件名称")
    asset = models.ForeignKey("Asset", blank=True, null=True, on_delete=models.SET_NULL)  # 当资产审批成功时有这项数据
    new_asset = models.ForeignKey("NewAssetApprovalZone", blank=True, null=True, on_delete=models.SET_NULL)  # 当资产审批失败时有这项数据
    event_type = models.SmallIntegerField(choices=event_type_choice, default=0, verbose_name="事件类型")
    component = models.CharField(max_length=256, blank=True, null=True, verbose_name="事件子项")
    detail = models.TextField("事件详情")
    date = models.DateTimeField(auto_now_add=True, verbose_name="事件时间")
    user = models.ForeignKey(Users, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="事件执行人")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "事件记录"
        verbose_name_plural = "事件记录"

class NewAssetApprovalZone(models.Model):
    """  新资产待审批区  """
    # asset_type_choice = (
    #     ("server", "服务器"),
    #     ("networkdevice", "网络设备"),
    #     ("storagedevice", "存储设备"),
    #     ("securitydevice", "安全设备"),
    #     ("software", "软件资产"),
    # )
    # sn = models.CharField(max_length=128, unique=True, verbose_name="资产SN号")
    # asset_type = models.CharField(choices=asset_type_choice, default="server", max_length=64, blank=True, null=True, verbose_name="资产类型")
    # manufacturer = models.CharField(max_length=64, blank=True, null=True, verbose_name="生产厂商")
    # model = models.CharField(max_length=128, blank=True, null=True, verbose_name="型号")
    # ram_size = models.PositiveIntegerField(blank=True, null=True, verbose_name="内存大小")
    # cpu_model = models.CharField(max_length=128, blank=True, null=True, verbose_name="CPU型号")
    # cpu_count = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="物理CPU数量")
    # cpu_core_count = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="CPU核心数量")
    # os_distribution = models.CharField(max_length=64, blank=True, null=True, verbose_name="发行商")
    # os_type = models.CharField(max_length=64, blank=True, null=True, verbose_name="系统类型")
    # os_release = models.CharField(max_length=64, blank=True, null=True, verbose_name="操作系统版本号")

    asset = models.ForeignKey("Asset", blank=True, null=True, on_delete=models.SET_NULL)  # 关联待审批资产
    approved = models.BooleanField(default=False, verbose_name="是否审批")
    # approved_by = models.ForeignKey(User, null=True, verbose_name="审批人", related_name='approved_by',on_delete=models.SET_NULL)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="汇报日期")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新日期")

    data = models.TextField("资产数据")  # 此字段必填

    def __str__(self):
        return self.data

    class Meta:
        verbose_name = "新上线待批准资产"
        verbose_name_plural = "新上线待批准资产"
        ordering = ["-create_time"]
