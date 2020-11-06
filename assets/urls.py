from django.urls import path
from assets import views

app_name = 'assets'

urlpatterns = [
    path('report/', views.report, name='report'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("index/", views.index, name="index"),
    path("detail/<int:asset_id>/", views.detail, name="detail"),
    path("event/", views.event, name="event"),
    path("asset_list/<str:asset_type>", views.asset_list, name="asset_list"),
    path("asset_manage_update/<int:asset_id>/", views.asset_manage_update, name="asset_manage_update"),
    path("asset_manage_new/<str:asset_type>", views.asset_manage_new, name="asset_manage_new"),
    # path("stgmanage/", views.storagedevice_manage, name="stgmanage"),
    # path("srtmanage/", views.securitydevice_manage, name="srtmanage"),
    # path("softmanage/", views.software_manage, name="softmanage"),

    # path("idcmanage/", views.software_manage, name="idcmanage"),
    # path("bsumanage/", views.software_manage, name="bsumanage"),
    # path("mftmanage/", views.software_manage, name="mftmanage"),
    # path("contmanage/", views.software_manage, name="contmanage"),
    # path("tagmanage/", views.software_manage, name="tagmanage"),

    path("", views.dashboard),
]