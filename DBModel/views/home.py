from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse

import random;

from website import settings
from DBModel import models

from release.base import *;

from _Global import _GG;

# 首页请求
@csrf_exempt
def home(request):
    _GG("Log").d("home GET :", request.GET, "; POST :", request.POST);
    if "isGetRecommendData" in request.POST:
        return JsonResponse(getRecommendData(request));
    isHasNewestInstaller, newestInstaller = getInstallerData()
    return render(request, "home.html", {
        "MAIN_HOME_TITLE":settings.MAIN_HOME_TITLE,
        "MAIN_HOME_URL":settings.MAIN_HOME_URL,
        "RESOURCE_URL" : settings.RESOURCE_URL,
        "HOME_TITLE": settings.HOME_TITLE,
        "HOME_URL": settings.HOME_URL,
        "HEAD_TITLE": settings.HOME_TITLE,
        "WIKI_URL": settings.WIKI_URL,
        "ptipInfoList" : getPtipData(),
        "isHasNewestInstaller" : isHasNewestInstaller,
        "newestInstaller" : newestInstaller,
        "recommendData" : getRecommendData(request),
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
    if len(retList) > 0:
        return True, retList[0];
    return False, None;

# 获取平台数据
def getPtipData():
    ptipList = models.Ptip.objects.filter(status = Status.Released.value).order_by('-base_version', '-time');
    return [{
            "version" : ptipInfo.version,
            "url" : ptipInfo.file_path.url,
            "changelog" : ptipInfo.changelog,
            "uploadTime" : ptipInfo.time,
    } for ptipInfo in ptipList];

# 获取今日推荐
def getRecommendInfoByArticle(articleInfo):
    ret = {
        "url" : settings.HOME_URL + f"/article?aid={articleInfo.id}",
        "thumbnail" : articleInfo.thumbnail and articleInfo.thumbnail.url or "",
        "title" : articleInfo.title,
        "subTitle" : articleInfo.sub_title,
        "description" : articleInfo.sketch,
        "author" :  articleInfo.uid.name,
        "badge" : "文章",
    };
    if articleInfo.atype == ArticleType.Tool.value:
        tools = articleInfo.tool_set.all();
        if len(tools) > 0 :
            tkey = tools[0].tkey;
            ret["url"] = settings.HOME_URL + f"/detail?t={tkey}";
            ret["badge"] = "工具";
        else:
            _GG("Log").w(f"Invalid tool's article[id={articleInfo.id}]!");
    return ret;

# 获取今日推荐
def getRecommendData(request):
    limit = 9;
    allInfoList = models.Article.objects.all();
    total = len(allInfoList);
    interval = int(total / limit);
    if interval > 0:
        tmpTotal = total + (limit - total % limit) % limit;
        def getNextIdx(curIdx):
            nextIdx = (curIdx + interval) % tmpTotal;
            if nextIdx == nextIdx % interval and interval > 1:
                nextIdx += 1;
            while nextIdx >= total:
                nextIdx = (nextIdx + interval) % tmpTotal;
            return nextIdx;
        # 获取开始下标
        startIdx = random.randint(0, total);
        if "rlStartIdx" in request.POST:
            try:
                rlStartIdx = int(request.POST["rlStartIdx"]);
                if 0 <= rlStartIdx <= total:
                    startIdx = rlStartIdx;
            except Exception as e:
                _GG("Log").w(e);
        # 获取返回列表
        _GG("Log").d("GetRecommendData params:", total, interval, tmpTotal, startIdx);
        retInfoList, idxList = [], [];
        while len(retInfoList) < limit:
            if startIdx in idxList:
                break;
            # 添加返回信息
            retInfoList.append(getRecommendInfoByArticle(allInfoList[startIdx]));
            idxList.append(startIdx);
            # 获取下一个下标
            startIdx = getNextIdx(startIdx);
        return {
            "startIdx" : startIdx,
            "htmlData" : bytes.decode(render(request, "tilelist.html", {"infoList" : retInfoList}).content),
        };
    return {
        "startIdx" : 0,
        "htmlData" : bytes.decode(render(request, "tilelist.html", {
            "infoList" : [getRecommendInfoByArticle(articleInfo) for articleInfo in allInfoList[:limit]],
        }).content),
    };
