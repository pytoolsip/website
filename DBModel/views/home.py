from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse

import random;

from website import settings
from DBModel import models

from release.base import *;

# 首页请求
@csrf_exempt
def home(request):
    if "isGetRecommendList" in request.POST:
        return JsonResponse(getRecommendList(request));
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
        "recommendList" : getRecommendList(request),
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
def getRecommendList(request):
    limit = 9;
    allInfoList = models.Article.objects.all();
    # total = len(allInfoList);
    # if total > limit:
    #     startIdx, interval, curIdx = random.randint(0, total), random.randint(0, total), 0;
    #     try:
    #         startIdx, interval, curIdx = int(request.POST.get("rlStartIdx", "0")), int(request.POST.get("rlInterval", "1")), int(request.POST.get("rlCurIdx", "0"));
    #         retInfoList = [];
    #         while len(retInfoList) < limit:
    #             curIdx = (curIdx + interval) % total;
    #             if curIdx == startIdx:
    #                 curIdx++
    #                 startIdx++
    #                 continue;
    #             # 构造返回信息
    #             articleInfo = allInfoList[curIdx];
    #             retInfo = {
    #                 "url" : settings.HOME_URL + f"/article?aid={articleInfo.id}",
    #                 "thumbnail" : articleInfo.thumbnail and articleInfo.thumbnail.url or "",
    #                 "title" : articleInfo.title,
    #                 "subTitle" : articleInfo.sub_title,
    #                 "description" : articleInfo.sketch,
    #             };
    #             retInfoList.append();
    #         return {
    #             "startIdx" : startIdx,
    #             "interval" : interval,
    #             "curIdx" : curIdx,
    #             "infoList" : retInfoList,
    #         };
    #         # return [{
    #         #     "id" : articleInfo.id,
    #         #     "title" : articleInfo.title,
    #         #     "subTitle" : articleInfo.sub_title,
    #         #     "thumbnail" : articleInfo.thumbnail and articleInfo.thumbnail.url or "",
    #         #     "sketch" : articleInfo.sketch,
    #         #     "time" :  articleInfo.time,
    #         #     "author" :  articleInfo.uid.name,
    #         #     "content" : articleInfo.cid.content,
    #         # } for articleInfo in articleInfoList];
    #     except Exception as e:
    #         _GG("Log").w(e);
    return [getRecommendInfoByArticle(articleInfo) for articleInfo in allInfoList[:limit]];
