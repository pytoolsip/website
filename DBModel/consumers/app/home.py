from django.db.models import Q;

from DBModel import models;

from DBModel.views.release.base import *;

from _Global import _GG;

reqArticleLimit = 8;
reqUserLimit = 8;

# 请求所有文章
def reqAllArticles(ctx, msg):
    article = None;
    try:
        aid = msg.get("startId", -1);
        if "endId" in msg:
            aid = msg["endId"]
        article = models.Article.objects.get(id = aid);
    except Exception as e:
        _GG("Log").w(e);
    limit = reqArticleLimit;
    if article:
        if "endId" in msg:
            articleList = models.Article.objects.filter(Q(time_gte = article.time) | (Q(time = article.time) & Q(id__gte = article.id))).order_by("-time", "-id");
            limit = len(articleList);
        else:
            articleList = models.Article.objects.filter(Q(time_lte = article.time) | (Q(time = article.time) & Q(id__lte = article.id))).order_by("-time", "-id");
    else:
        articleList = models.Article.objects.filter(id__lte = startId).order_by("-time", "-id");
    if "endId" not in msg and len(articleList) <= reqArticleLimit:
        limit = len(articleList);
    return {
        "items" : [convertArticleInfo(articleInfo) for articleInfo in articleList[:limit]],
        "isInTheEnd" : len(articleList) <= reqArticleLimit,
    };

# 转换文章信息
def convertArticleInfo(articleInfo):
    return {
        "id" : articleInfo.id,
        "title" : articleInfo.title,
        "subTitle" : articleInfo.sub_title,
        "thumbnail" : articleInfo.thumbnail,
        "sketch" : articleInfo.sketch,
        "time" : articleInfo.time,
        "author" : articleInfo.uid.name,
        "author_pic" : articleInfo.uid.img,
        "atype" : articleInfo.atype,
        "readingVolume" : articleInfo.reading_volume,
    };

# 请求所有用户
def reqAllUsers(ctx, msg):
    user = None;
    try:
        uid = msg.get("startId", -1);
        if "endId" in msg:
            uid = msg["endId"]
        user = models.User.objects.get(id = uid);
    except Exception as e:
        _GG("Log").w(e);
    limit = reqUserLimit;
    if user:
        if "endId" in msg:
            userList = models.User.objects.filter(Q(time_gte = user.time) | (Q(time = user.time) & Q(id__gte = user.id))).order_by("-time", "-id");
            limit = len(userList);
        else:
            userList = models.User.objects.filter(Q(time_lte = user.time) | (Q(time = user.time) & Q(id__lte = user.id))).order_by("-time", "-id");
    else:
        userList = models.User.objects.filter(id__lte = startId).order_by("-time", "-id");
    if "endId" not in msg and len(userList) <= reqUserLimit:
        limit = len(userList);
    items = [];
    for userInfo in userList[:limit]:
        item = {
            "id" : userInfo.id,
            "name" : userInfo.name,
            "pic" : userInfo.img,
            "isFollowed" : False,
            "followCount" : 0,
            "articleCount" : 0,
            "time" : userInfo.time,
            "author" : userInfo.uid.name,
            "atype" : userInfo.atype,
        };
        item["articleCount"] = len(models.Article.objects.filter(uid = userInfo, atype = ArticleType.Article.value));
        item["toolCount"] = len(models.Article.objects.filter(uid = userInfo, atype = ArticleType.Tool.value));
        articleList = models.Article.objects.filter(uid = userInfo).order_by("-time", "-id");
        if len(articleList) > 0:
            item["content"] = convertArticleInfo(articleList[0]);
            item["isMedia"] = True;
        else:
            item["content"] = userInfo.bio;
            item["isText"] = True;
        items.append(item);
    return {
        "items" : items,
        "isInTheEnd" : len(userList) <= reqUserLimit,
    };
