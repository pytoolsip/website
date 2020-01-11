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
    result = {
        "MAIN_HOME_TITLE":settings.MAIN_HOME_TITLE,
        "MAIN_HOME_URL":settings.MAIN_HOME_URL,
        "RESOURCE_URL" : settings.RESOURCE_URL,
        "HOME_TITLE": settings.HOME_TITLE,
        "HOME_URL": settings.HOME_URL,
        "HEAD_TITLE": "文章列表",
        "searchText" : searchText,
        "isSearchNone" : False,
        "articleInfoList" : [],
    };
    # 根据searchText搜索文章信息列表
    result["articleInfoList"].extend(serachArticleListByTitle(searchText));
    # 判断是否搜索出了结果
    if searchText:
        result["isSearchNone"] = len(result["articleInfoList"]) == 0;
    return render(request, "articlelist.html", result);

# 根据title搜索文章信息列表
def serachArticleListByTitle(title):
    articleInfoList = models.Article.objects.filter(title__icontains = title, atype = ArticleType.Article.value).order_by('-time');
    return [{
        "id" : articleInfo.id,
        "title" : articleInfo.title,
        "subTitle" : articleInfo.sub_title,
        "thumbnail" : articleInfo.thumbnail and articleInfo.thumbnail.url or "",
        "sketch" : articleInfo.sketch,
        "time" :  articleInfo.time,
        "author" :  articleInfo.uid.name,
        "content" : articleInfo.cid.content,
    } for articleInfo in articleInfoList];