from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse

from website import settings
from DBModel import models

# 搜索页请求
@csrf_exempt
def search(request):
    select = request.POST.get("searchSelect", "name");
    text = request.POST.get("searchText", "");
    result = {
        "MAIN_HOME_TITLE":settings.MAIN_HOME_TITLE,
        "MAIN_HOME_URL":settings.MAIN_HOME_URL,
        "RESOURCE_URL" : settings.RESOURCE_URL,
        "HOME_TITLE": settings.HOME_TITLE,
        "HOME_URL": settings.HOME_URL,
        "HEAD_TITLE": "搜索工具",
        "isSearchNone" : False,
        "searchSelect" : select,
        "searchText" : text,
        "searchObject" : "工具",
        "toolInfoList" : [],
        "userInfoList" : [],
    };
    # 校验提交的数据
    if "searchSelect" not in request.POST:
        return render(request, "toollist.html", result);
    # 从数据库中查找数据
    if select == "id":
        # 根据tkey获取工具信息
        ret, toolInfo = getToolInfoByTKey(text);
        if ret:
            result["toolInfoList"].append(toolInfo);
    elif select == "author":
        if request.POST.get("isSearchTools", False):
            # 根据userName获取工具信息列表
            ret, toolInfoList = getToolInfoListByUserName(text);
            if ret:
                result["toolInfoList"].extend(toolInfoList);
        else:
            # 根据userName搜索玩家信息列表
            ret, userInfoList = serachUserInfoListByName(text);
            if ret:
                result["userInfoList"].extend(userInfoList);
            result["searchObject"] = "用户";
    else:
        # 根据toolName搜索工具信息列表
        ret, toolInfoList = serachToolInfoListByName(text);
        if ret:
            result["toolInfoList"].extend(toolInfoList);
    # 判断是否搜索出了结果
    if len(result["toolInfoList"]) == 0 and len(result["userInfoList"]) == 0 and text:
        result["isSearchNone"] = True;
    return render(request, "search.html", result);

# 根据tkey获取工具信息
def getToolInfoByTKey(tkey):
    toolInfos = models.Tool.objects.filter(tkey = tkey).order_by('-time');
    if len(toolInfos) > 0:
        toolInfo = toolInfos[0];
        return True, {
            "name" : toolInfo.name,
            "category" : toolInfo.category,
            "tkey" : toolInfo.tkey,
            "description" : toolInfo.description,
            "downloadCount" : toolInfo.download or 0,
            "score" : toolInfo.score or 0.0,
            "author" :  toolInfo.uid.name,
            "uploadTime" :  toolInfo.time,
        };
    return False, {};

# 根据userName获取工具信息列表
def getToolInfoListByUserName(name):
    userInfos = models.User.objects.filter(name = name);
    if len(userInfos) > 0:
        toolInfoList = models.Tool.objects.filter(uid = userInfos[0]).order_by('-time');
        return True, [{
            "name" : toolInfo.name,
            "category" : toolInfo.category,
            "tkey" : toolInfo.tkey,
            "description" : toolInfo.description,
            "downloadCount" : toolInfo.download or 0,
            "score" : toolInfo.score or 0.0,
            "author" :  toolInfo.uid.name,
            "uploadTime" :  toolInfo.time,
        } for toolInfo in toolInfoList];
    return False, [];

# 根据userName搜索玩家信息列表
def serachUserInfoListByName(name):
    userInfoList = models.User.objects.filter(name__icontains = name).order_by('-time');
    if len(userInfoList) > 0:
        return True, [{
            "name" : userInfo.name,
            "email" : userInfo.email,
            "img" : userInfo.img.url,
            "bio" : userInfo.bio,
        } for userInfo in userInfoList];
    return False, [];

# 根据toolName搜索工具信息列表
def serachToolInfoListByName(name):
    toolInfoList = models.Tool.objects.filter(name__icontains = name).order_by('-time');
    if len(toolInfoList) > 0:
        return True, [{
            "name" : toolInfo.name,
            "category" : toolInfo.category,
            "tkey" : toolInfo.tkey,
            "description" : toolInfo.description,
            "downloadCount" : toolInfo.download or 0,
            "score" : toolInfo.score or 0.0,
            "author" :  toolInfo.uid.name,
            "uploadTime" :  toolInfo.time,
        } for toolInfo in toolInfoList];
    return False, [];