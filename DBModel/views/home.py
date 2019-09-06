from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse

from website import settings
from DBModel import models

from release.base import *;

# 首页请求
@csrf_exempt
def home(request):
    isHasNewestInstaller, newestInstaller = getInstallerData()
    return render(request, "home.html", {
        "HOME_URL": settings.HOME_URL,
        "ptipInfoList" : getPtipData(),
        "isHasNewestInstaller" : isHasNewestInstaller,
        "newestInstaller" : newestInstaller,
    });

# 获取安装程序数据
def getInstallerData():
    installerList = models.Installer.objects.all().order_by('-base_version', '-time');
    retList = [{
            "version" : installerInfo.version,
            "url" : installerInfo.file_path.url,
            "changelog" : installerInfo.changelog,
            "uploadTime" : installerInfo.time,
    } for installerInfo in installerList];
    return len(retList) > 0, retList[0];

# 获取平台数据
def getPtipData():
    ptipList = models.Ptip.objects.filter(status = Status.Released.value).order_by('-base_version', '-time');
    return [{
            "version" : ptipInfo.version,
            "url" : ptipInfo.file_path.url,
            "changelog" : ptipInfo.changelog,
            "uploadTime" : ptipInfo.time,
    } for ptipInfo in ptipList];