from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

import json
from assets import models
from assets import asset_handler
from django.shortcuts import get_object_or_404
# Create your views here.

@login_required
@csrf_exempt
def report(request):
    """
    通过csrf_exempt装饰器，跳过Django的csrf安全机制，让post的数据能被接收，但这又会带来新的安全问题。
    可以在客户端，使用自定义的认证token，进行身份验证。这部分工作，请根据实际情况，自己进行。
    :param request:
    :return:
    """
    if request.method == "POST":
        asset_data = request.POST.get("asset_data")
        data = json.loads(asset_data)
        # 各种数据检查，请自行添加和完善
        if not data:
            return HttpResponse("没有数据!")
        if not issubclass(dict, type(data)):
            return HttpResponse("数据必须为字典格式！")
        # 是否携带了关键的sn号
        sn = data.get('sn', None)
        if sn:
            # 进入审批流程
            # 首先判断是否在上线资产中存在该sn
            asset_obj = models.Asset.objects.filter(sn=sn, status__gt=0)
            if asset_obj:
                # 进入已上线资产的数据更新流程
                udpate_asset = asset_handler.UpdateAsset(request, asset_obj[0], data)
                return HttpResponse("资产数据已经更新！")
            else:
                obj = asset_handler.NewAsset(request, data)
                response = obj.add_to_new_assets_zone()
                return HttpResponse(response)
        else:
            return HttpResponse("没有资产sn序列号，请检查数据！")
    return HttpResponse('200 ok')


        # print(asset_data)
        # return HttpResponse("成功收到数据！")

@login_required
def index(request):
    assets = models.Asset.objects.all()
    return render(request, "assets/index.html", locals())

@login_required
def dashboard(request):
    total = models.Asset.objects.count()
    upline = models.Asset.objects.filter(status=1).count()
    offline = models.Asset.objects.filter(status=2).count()
    unknown = models.Asset.objects.filter(status=3).count()
    breakdown = models.Asset.objects.filter(status=4).count()
    backup = models.Asset.objects.filter(status=5).count()
    up_rate = round(upline/total*100) if total != 0 else 0      # 当total为0时直接返回0，防止 除数为零 报错
    off_rate = round(offline/total*100) if total != 0 else 0
    un_rate = round(unknown/total*100) if total != 0 else 0
    bd_rate = round(breakdown/total*100) if total != 0 else 0
    bu_rate = round(backup/total*100) if total != 0 else 0
    server_number = models.Server.objects.count()
    networkdevice_number = models.NetworkDevice.objects.count()
    storagedevice_number = models.StorageDevice.objects.count()
    securitydevice_number = models.SecurityDevice.objects.count()
    software_number = models.Software.objects.count()

    return render(request, "assets/dashboard.html", locals())

@login_required
def detail(request, asset_id):
    """
    以显示服务器类型资产详细为例，安全设备、存储设备、网络设备等参照此例。
    :param request:
    :param asset_id:
    :return:
    """
    asset = get_object_or_404(models.Asset, id=asset_id)
    # 根据asset_type 拼接对应的detail
    html_templates = "assets/detail/%s_detail.html" % asset.asset_type
    return render(request, html_templates, locals())

@login_required
def event(request):
    """用于查询事件记录"""
    events = models.EventLog.objects.all()
    return render(request, "assets/report/event.html", locals())

@login_required
def asset_list(request, asset_type):
    """
    不同资产类型列表页面
    """
    asset_type_choice = [
        'server',
        'networkdevice',
        'storagedevice',
        'securitydevice',
        'software'
    ]

    if asset_type in asset_type_choice:
        # 根据 asset_type 拼接出页面名称
        asset_list_page = "assets/manage/%s_list.html" % asset_type

        # if asset_type == "server":
        #     servers = models.Server.objects.all()
        # elif asset_type == "networkdevice":
        #     networkdevices = models.NetworkDevice.objects.all()
        # elif asset_type == "storagedevice":
        #     storagedevices = models.StorageDevice.objects.all()
        # elif asset_type == "securitydevice":
        #     securitydevices = models.SecurityDevice.objects.all()
        # elif asset_type == "software":
        #     software = models.Software.objects.all()
        # elif asset_type == "software":
        #     businessunit = models.BusinessUnit.objects.all()
        ## elif asset_type == "6":
        ##     manufacturer = models.Manufacturer.objects.all()
        ## elif asset_type == "7":
        ##     contracts = models.Contract.objects.all()
        ## elif asset_type == "8":
        ##     idcs = models.IDC.objects.all()
        ## elif asset_type == "9":
        ##     tags = models.Tag.objects.all()
    else:
        return "资源类型错误！"

    assets = models.Asset.objects.filter(asset_type=asset_type, status__lt=7)
    return render(request, asset_list_page, locals())

# def server_list(request):
#     servers = models.Server.objects.all()
#     return render(request, "assets/manage/server_list.html", locals())

@login_required
def asset_manage_new(request, asset_type):
    if request.method == "POST":

        # data = dict()
        # # general assets info
        # data["asset_type"] = asset_type
        # data["business_unit"] = request.POST.get("business_unit")
        # data["name"] = request.POST.get("name")
        # data["sn"] = request.POST.get("sn")
        # data["status"] = request.POST.get("status")
        # data["manufacturer"] = request.POST.get("manufacturer")
        # data["manage_ip"] = request.POST.get("manage_ip")
        # data["idc"] = request.POST.get("idc")
        # data["admin"] = request.POST.get("admin")
        # data["approved_by"] = request.POST.get("approved_by")
        # data["contract"] = request.POST.get("contract")
        # data["price"] = request.POST.get("price")
        # data["purchase_day"] = request.POST.get("purchase_day")
        # data["expire_day"] = request.POST.get("expire_day")
        # data["tags"] = request.POST.get("tags")
        # data["remark"] = request.POST.get("remark")

        # data = dict(request.POST.lists())     # request 的 POST、GET 属性都是 QueryDict 实例，lists() 是 QueryDict 的方法，格式与dict控件兼容，可以用于以字典的形式返回所有 POST 中的值，此处用于直接将request 的 form 表单中的所有值转换为字典类型
        data = dict(request.POST.dict())        # lists() 转换为 dict 对象后，每一个item 的value 均为 list 类型；使用 dict() 方法 转换后的value 为 string 类型，但要对真实存在的list value 进行处理
        # request.POST.dict() 处理 list 类型的 value时只返回 list的最后一个值，需要额外处理
        tags = request.POST.getlist("tags")
        data["tags"] = tags

        # 各类别独有信息处理
        obj = asset_handler.NewAsset(request, data)
        response = obj.add_to_new_assets_zone()

        created_by = request.POST.get("created_by")
        # 手动录入提交，成功返回资产列表，失败返回录入页面重新修改
        if created_by == "manual":
            if response:
                assets = models.Asset.objects.filter(asset_type=asset_type)
                asset_list_page = "assets/manage/%s_list.html" % asset_type
                return render(request, asset_list_page, locals())
            else:
                asset_manage_page = "assets/manage/%s_manage_new.html" % asset_type
                businessunit = models.BusinessUnit.objects.all()
                manufacturer = models.Manufacturer.objects.all()
                tags = models.Tag.objects.all()
                users = ['张三', '李四']
                idcs = models.IDC.objects.all()
                contract = models.Contract.objects.all()
                return render(request, asset_manage_page, locals())
        # 自动录入，即 client 传输过来的数据，直接返回 response，也即 True/False
        else:
            return HttpResponse(response)
    else:
        asset_manage_page = "assets/manage/%s_manage_new.html" % asset_type
        businessunit = models.BusinessUnit.objects.all()
        manufacturer = models.Manufacturer.objects.all()
        tags = models.Tag.objects.all()
        users = ['张三', '李四']
        idcs = models.IDC.objects.all()
        contract = models.Contract.objects.all()

        return render(request, asset_manage_page, locals())

@login_required
def asset_manage_update(request, asset_id):
    """
    管理如下资产的修改
    服务器 server
    网络设备 networkdevice
    安全设备 securitydevice
    存储设备 storagedevice
    软件 software
    """
    asset = models.Asset.objects.get(pk=asset_id)
    asset_type = asset.asset_type
    asset_list_page = "assets/manage/%s_list.html" % asset_type
    asset_manage_page = "assets/manage/%s_manage.html" % asset_type

    if request.method == "POST":

        data = dict(request.POST.dict())
        tags = request.POST.getlist("tags")
        data["tags"] = tags

        obj = asset_handler.UpdateAsset(request, asset, data)
        response = obj.asset_update()
        print("表单提交 %s" % asset_type)

        return redirect("/assets/asset_list/%s" % asset_type)
    ##  asset_data = request.POST.get("asset_data")
    ##  data = json.loads(asset_data)
    ##  # 各种数据检查，请自行添加和完善
    ##  if not data:
    ##      return HttpResponse("没有数据!")
    ##  if not issubclass(dict, type(data)):
    ##      return HttpResponse("数据必须为字典格式！")
    ##  # 是否携带了关键的sn号
    ##  sn = data.get('sn', None)
    ##  if sn:
    ##      # 进入审批流程
    ##      # 首先判断是否在上线资产中存在该sn
    ##      asset_obj = models.Asset.objects.filter(sn=sn)
    ##      if asset_obj:
    ##          # 进入已上线资产的数据更新流程
    ##          udpate_asset = asset_handler.UpdateAsset(request, asset_obj[0], data)
    ##          return HttpResponse("资产数据已经更新！")
    ##      else:
    ##          obj = asset_handler.NewAsset(request, data)
    ##          response = obj.add_to_new_assets_zone()
    ##          return HttpResponse(response)
    ##  else:
    ##      return HttpResponse("没有资产sn序列号，请检查数据！")
    else:
        # 用于 修改页面的下拉框，后续改为从 Redis 获取
        # server = models.Server.objects.get(asset_id=asset_id)
        asset = models.Asset.objects.get(pk=asset_id)
        businessunit = models.BusinessUnit.objects.all()
        manufacturer = models.Manufacturer.objects.all()
        tags = models.Tag.objects.all()
        users = ['张三', '李四']
        idcs = models.IDC.objects.all()
        contract = models.Contract.objects.all()

        # 根据asset_type 拼接出页面名称
        return render(request, asset_manage_page, locals())

@login_required
def asset_manage_del(request, asset_id):
    asset = get_object_or_404(models.Asset, pk=asset_id)
    old_status = asset.status
    full_path = request.get_full_path()
    try:
        asset.status = 7
        asset.save()
        message = "%s %s 已删除" % (asset.asset_type,asset.name)
        return redirect("/assets/asset_list/%s" % asset.asset_type)
    except Exception as e:
        asset.status = old_status
        asset.save()
        message = "%s %s 删除失败" % (asset.asset_type, asset.name)
        return redirect("/assets/asset_list/%s" % asset.asset_type)

# def networkdevice_manage(request):
#     networks = models.NetworkDevice.objects.all()
#     return render(request, "assets/manage/networkdevice_manage.html", locals())
#
# def storagedevice_manage(request):
#     sotrages = models.StorageDevice.objects.all()
#     return render(request, "assets/manage/storagedevice_manage.html", locals())
#
# def securitydevice_manage(request):
#     securities = models.SecurityDevice.objects.all()
#     return render(request, "assets/manage/securitydevice_manage.html", locals())
#
# def software_manage(request):
#     software = models.Software.objects.all()
#     return render(request, "assets/manage/software_manage.html", locals())

@login_required
def idc_manage(request):
    idcs = models.IDC.objects.all()
    return render(request, "assets/manage/idc_manage.html", locals())

@login_required
def manufacturer_manage(request):
    manufacturer = models.Manufacturer.objects.all()
    return render(request, "assets/manage/manufacturer_manage.html", locals())

@login_required
def businessunit_manage(request):
    businessunits = models.BusinessUnit.objects.all()
    return render(request, "assets/manage/businessunit_manage.html", locals())

@login_required
def contract_manage(request):
    contracts = models.Contract.objects.all()
    return render(request, "assets/manage/contract_manage.html", locals())

@login_required
def tag_manage(request):
    tags = models.Tag.objects.all()
    return render(request, "assets/manage/tag_manage.html", locals())

@login_required
def new_asset_approval_list(request):
    assets = models.Asset.objects.filter(status=0)
    return render(request, "assets/approval.html", locals())

@login_required
def new_asset_approval_zone(request, asset_id):
    asset = get_object_or_404(models.NewAssetApprovalZone, asset_id=asset_id)

    try:
        asset.approved = True   # 修改 NewAssetApprovalZone 表 状态为 已审批
        asset.asset.status = 6  # 修改 Asset 表 status=6 待审批
        asset.save()
        asset.asset.save()
        # asset = models.NewAssetApprovalZone.objects.filter(asset_id=asset_id)
        # asset.update(approved=True)
        assets = models.Asset.objects.filter(status=0)
        return render(request, "assets/approval.html", locals())
    except Exception as e:
        asset.approved = False
        asset.asset.status = 0
        asset.save()
        asset.asset.save()

        assets = models.Asset.objects.filter(status=0)
        return render(request, "assets/approval.html", locals())