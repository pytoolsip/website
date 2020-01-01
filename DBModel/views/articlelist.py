from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse

from website import settings
from DBModel import models
from utils import base_util

from release.base import *

from _Global import _GG;

# 搜索页请求
@csrf_exempt
def articlelist(request):
    request.encoding = "utf-8";
    _GG("Log").d("articlelist GET :", request.GET, "; POST :", request.POST, "; FILES :", request.FILES);
    # 搜索内容
    searchText = request.POST.get("searchText", "");
    result = {"HOME_URL": settings.HOME_URL, "RESOURCE_URL" : settings.RESOURCE_URL, "searchText" : searchText, "isSearchNone" : False, "articleInfoList" : []};
    # 根据searchText搜索文章信息列表
    result["articleInfoList"].extend(serachToolListByTitle(searchText));
    # 判断是否搜索出了结果
    if searchText:
        result["isSearchNone"] = len(result["articleInfoList"]) == 0;
    return render(request, "articlelist.html", result);

# 根据toolName搜索工具信息列表
def serachToolListByTitle(title):
    articleInfoList = models.Article.objects.filter(title__icontains = title, atype = ArticleType.Article.value);
    return [{
        "id" : articleInfo.id,
        "title" : articleInfo.title,
        "subTitle" : articleInfo.sub_title,
        "thumbnail" : articleInfo.thumbnail,
        "sketch" : articleInfo.sketch,
        "time" :  articleInfo.time,
        "author" :  articleInfo.uid.name,
        "content" : articleInfo.cid.content,
    } for articleInfo in articleInfoList];