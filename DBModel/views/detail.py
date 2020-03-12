from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse

from website import settings

from DBModel import models

import userinfo;

from release.base import *

from _Global import _GG;

# 工具详情页
@csrf_exempt
@userinfo.checkLogined
def detail(request):
    request.encoding = "utf-8";
    _GG("Log").d("detail get :", request.GET, "detail post :", request.POST);
    tkey = request.GET.get("t", "");
    if "submit" in request.POST:
        result = {"isLoginFailed" : False, "isSuccess" : False};
        try:
            userAuth = request.userAuth;
            if userAuth:
                tool = models.Tool.objects.get(tkey = tkey);
                # 保存收藏
                if request.POST["submit"] == "collect":
                    result["isSuccess"] = doCollect(request.POST, userAuth, tool.aid);
                    return JsonResponse(result);
                # 保存评论
                if request.POST["submit"] == "comment":
                    result["isSuccess"] = doComment(request.POST, userAuth, tool.aid);
                    return JsonResponse(result);
            else:
                result["isLoginFailed"] = True;
        except Exception as e:
            _GG("Log").w(e);
        return JsonResponse(result);
    return render(request, "detail.html", getResultByTkey(tkey));

# 处理收藏
def doCollect(postData, userAuth, article):
    isCollect = postData.get("isCollect", "") == "true";
    try:
        collections = models.Collection.objects.filter(uid = userAuth.uid, aid = article);
        if isCollect and len(collections) == 0:
            c = models.Collection(uid = userAuth.uid, aid = article);
            c.save();
            return True;
        elif not isCollect and len(collections) > 0:
            collections.delete();
            return True;
    except Exception as e:
        _GG("Log").w(e);
    return False;

# 处理评论
def doComment(postData, userAuth, article):
    isSave = True;
    for k in ["score", "content"]:
        if k not in postData:
            isSave = False;
            break;
    if isSave:
        try:
            c = models.Comment(uid = userAuth.uid, aid = article, score = postData["score"], content = postData["content"], time = timezone.now());
            c.save();
            return True;
        except Exception as e:
            _GG("Log").w(e);
    return False;

# 根据tkey获取工具信息结果
def getResultByTkey(tkey):
    result = {
        "MAIN_HOME_TITLE":settings.MAIN_HOME_TITLE,
        "MAIN_HOME_URL":settings.MAIN_HOME_URL,
        "RESOURCE_URL" : settings.RESOURCE_URL,
        "HOME_TITLE": settings.HOME_TITLE,
        "HOME_URL": settings.HOME_URL,
        "HEAD_TITLE": "",
        "commentLenLimit" : 600,
    };
    toolInfos = models.ToolDetail.objects.filter(tkey = tkey).order_by('-time');
    if len(toolInfos) > 0:
        # 获取工具基础信息
        baseInfo = toolInfos[0].tkey;
        result["HEAD_TITLE"] = f"{baseInfo.name}[{baseInfo.category}]";
        result["hasTool"] = True;
        result["baseInfo"] = {
            "name" : baseInfo.name,
            "category" : baseInfo.category,
            "tkey" : baseInfo.tkey,
            "description" : baseInfo.description,
            "downloadCount" : baseInfo.download or 0,
            "score" : baseInfo.score or 0.0,
            "author" :  baseInfo.uid.name,
            "time" :  baseInfo.time,
            "thumbnail" : baseInfo.aid.thumbnail and baseInfo.aid.thumbnail.url or "",
            "content" : baseInfo.aid.cid.content,
        };
        # 是否收藏了工具
        collections = models.Collection.objects.filter(uid = baseInfo.uid, aid = baseInfo.aid);
        if len(collections) > 0:
            result["isCollect"] = True;
        # 工具列表
        result["toolInfoList"] = [{
            "version" : toolInfo.version,
            "IPBaseVersion" : toolInfo.ip_base_version,
            "url" : toolInfo.file_path.url,
            "changelog" : toolInfo.changelog,
            "uploadTime" :  toolInfo.time,
        } for toolInfo in toolInfos];
        # 评论信息
        cfg = models.Appconfig.objects.filter(ckey = "close_all_common");
        if len(cfg) > 0 and cfg[0].cval == "true":
            result["isCloseComment"] = True;
        elif baseInfo.aid.comment_state == CommentType.Close.value:
            result["isCloseComment"] = True;
        else:
            commentInfos = baseInfo.aid.comment_set.all().order_by("-time");
            result["commentInfoList"] = [{
                "user" : commentInfo.uid.name,
                "time" : commentInfo.time,
                "score" : commentInfo.score,
                "content" : commentInfo.content,
            } for commentInfo in commentInfos];
    return result;

# 文章页
@csrf_exempt
@userinfo.checkLogined
def article(request):
    request.encoding = "utf-8";
    _GG("Log").d("detail get :", request.GET, "detail post :", request.POST);
    try:
        aid = int(request.GET.get("aid", ""));
    except Exception as e:
        _GG("Log").w(e);
        aid = -1;
    if "submit" in request.POST:
        result = {"isLoginFailed" : False, "isSuccess" : False};
        try:
            userAuth = request.userAuth;
            if userAuth:
                article = models.Article.objects.get(id = aid);
                # 保存收藏
                if request.POST["submit"] == "collect":
                    result["isSuccess"] = doCollect(request.POST, userAuth, article);
                    return JsonResponse(result);
                # 保存评论
                if request.POST["submit"] == "comment":
                    result["isSuccess"] = doComment(request.POST, userAuth, article);
                    return JsonResponse(result);
            else:
                result["isLoginFailed"] = True;
        except Exception as e:
            _GG("Log").w(e);
        return JsonResponse(result);
    return render(request, "article.html", getResultByAid(aid));

# 根据tkey获取工具信息结果
def getResultByAid(aid):
    result = {
        "MAIN_HOME_TITLE":settings.MAIN_HOME_TITLE,
        "MAIN_HOME_URL":settings.MAIN_HOME_URL,
        "RESOURCE_URL" : settings.RESOURCE_URL,
        "HOME_TITLE": settings.HOME_TITLE,
        "HOME_URL": settings.HOME_URL,
        "HEAD_TITLE": "",
        "commentLenLimit" : 600,
    };
    articleInfos = models.Article.objects.filter(id = aid, atype = ArticleType.Article.value).order_by('-time');
    if len(articleInfos) > 0:
        # 获取工具基础信息
        articleInfo = articleInfos[0];
        result["HEAD_TITLE"] = f"{articleInfo.title}[{articleInfo.sub_title}]";
        result["hasArticle"] = True;
        result["articleInfo"] = {
            "title" : articleInfo.title,
            "subTitle" : articleInfo.sub_title,
            "thumbnail" : articleInfo.thumbnail and articleInfo.thumbnail.url or "",
            "time" :  articleInfo.time,
            "author" :  articleInfo.uid.name,
            "content" : articleInfo.cid.content,
        };
        # 是否收藏了工具
        collections = models.Collection.objects.filter(uid = articleInfo.uid, aid = articleInfo);
        if len(collections) > 0:
            result["isCollect"] = True;
        # 评论信息
        cfg = models.Appconfig.objects.filter(ckey = "close_all_common");
        if len(cfg) > 0 and cfg[0].cval == "true":
            result["isCloseComment"] = True;
        elif articleInfo.comment_state == CommentType.Close.value:
            result["isCloseComment"] = True;
        else:
            commentInfos = articleInfo.comment_set.all().order_by("-time");
            result["commentInfoList"] = [{
                "user" : commentInfo.uid.name,
                "time" : commentInfo.time,
                "score" : commentInfo.score,
                "content" : commentInfo.content,
            } for commentInfo in commentInfos];
    return result;
