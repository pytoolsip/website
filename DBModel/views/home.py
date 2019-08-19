from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse

from DBModel import models

# 首页请求
def home(request):
    ptipInfoList, isHasNewestPtip, newestPtip = getPtipData()
    return render(request, "home.html", {
        "toolInfoList" : getToolInfoList(),
        "ptipInfoList" : ptipInfoList,
        "isHasNewestPtip" : isHasNewestPtip,
        "newestPtip" : newestPtip,
    });

# 获取平台数据
def getPtipData():
    ptipInfos = models.Ptip.objects.order_by('time');
    ptipInfoList = [{
            "version" : ptipInfo.version,
            "url" : ptipInfo.file_path.url,
            "changelog" : ptipInfo.changelog,
            "uploadTime" : ptipInfo.time,
    } for ptipInfo in ptipInfos];
    # 最新平台信息
    isHasNewest, newestPtip = False, {};
    if len(ptipInfoList) > 0:
        isHasNewest, newestPtip = True, ptipInfoList[-1];
    return ptipInfoList, isHasNewest, newestPtip;

# 获取工具信息列表
def getToolInfoList():
    toolInfoList = models.Tool.objects.order_by('time');
    return [{
        "name" : toolInfo.name,
        "category" : toolInfo.category,
        "tkey" : toolInfo.tkey,
        "description" : toolInfo.description,
        "downloadCount" : toolInfo.download or 0,
        "score" : toolInfo.score or 0.0,
        "author" :  toolInfo.uid.name,
        "uploadTime" :  toolInfo.time,
    } for toolInfo in toolInfoList];