from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse

from website import settings
from DBModel import models
from utils import base_util

from search import search

from _Global import _GG;

TlKeyMap = {
    "all" : "",
    "development" : "开发工具",
    "product" : "产品工具",
    "entertainment" : "娱乐工具",
}

# 搜索页请求
@csrf_exempt
def toollist(request):
    request.encoding = "utf-8";
    _GG("Log").d("toollist GET :", request.GET, "; POST :", request.POST, "; FILES :", request.FILES);
    # 获取工具列表键值
    tlkey = request.GET.get("k", "all");
    if tlkey not in TlKeyMap:
        tlkey = "all";
    # 校验提交的数据
    if "searchText" in request.POST:
        # 判断是否为所有工具模块
        if tlkey == "all":
            return search(request);
        # 搜索其他模块
        searchText = request.POST["searchText"];
        title = TlKeyMap[tlkey];
        result = {
            "MAIN_HOME_TITLE":settings.MAIN_HOME_TITLE,
            "MAIN_HOME_URL":settings.MAIN_HOME_URL,
            "RESOURCE_URL" : settings.RESOURCE_URL,
            "HOME_TITLE": settings.HOME_TITLE,
            "HOME_URL": settings.HOME_URL,
            "HEAD_TITLE": f"搜索{title}工具",
            "tlkey" : tlkey,
            "searchText" : searchText,
            "isSearchNone" : False,
            "toolInfoList" : [],
        };
        # 根据searchText搜索工具信息列表
        result["toolInfoList"].extend(serachToolListByName(tlkey, searchText));
        # 判断是否搜索出了结果
        if searchText:
            result["isSearchNone"] = len(result["toolInfoList"]) == 0;
        return render(request, "toollist_item.html", result);
    return render(request, "toollist.html", {
        "MAIN_HOME_TITLE":settings.MAIN_HOME_TITLE,
        "MAIN_HOME_URL":settings.MAIN_HOME_URL,
        "RESOURCE_URL" : settings.RESOURCE_URL,
        "HOME_TITLE": settings.HOME_TITLE,
        "HOME_URL": settings.HOME_URL,
        "HEAD_TITLE": f"工具列表",
        "tlkey" : tlkey,
    });

# 根据toolName搜索工具信息列表
def serachToolListByName(tlkey, name):
    toolInfoList = models.Tool.objects.filter(name__icontains = name, category__regex = "^%s/"%TlKeyMap[tlkey]).order_by('-time');
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