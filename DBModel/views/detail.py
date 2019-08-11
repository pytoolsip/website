from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse

from DBModel import models

from _Global import _GG;

# 工具详情页
@csrf_exempt
def detail(request):
    request.encoding = "utf-8";
    tkey = request.GET.get("t", "");
    try:
        user = models.User.objects.get(id = request.POST.get("uid", -1));
        tool = models.Tool.objects.get(tkey = tkey);
        # 保存收藏
        doCollection(request.POST, user, tool);
        # 保存评论
        doComment(request.POST, user, tool);
    except Exception as e:
        _GG("Log").d(e);
    return render(request, "detail.html", getToolResultByTkey(tkey));

# 处理收藏
def doCollection(postData, user, tool):
    if "isCollect" in postData:
        collections = models.Collection.objects.filter(uid = user.id, tkey = tool.tkey);
        if postData["isCollect"] and len(collections) == 0:
            c = models.Collection(uid = user, tkey = tool);
            c.save();
        elif not postData["isCollect"] and len(collections) > 0:
            collections.delete();

# 处理评论
def doComment(postData, user, tool):
    isSave = True;
    for k in ["uid", "score", "content"]:
        if k not in postData:
            isSave = False;
            break;
    if isSave:
        c = models.Comment(uid = user, tkey = tool, score = postData["score"], content = postData["content"], time = timezone.now());
        c.save();

# 根据tkey获取工具信息结果
def getToolResultByTkey(tkey):
    result = {"hasTool" : False};
    toolInfos = models.ToolDetail.objects.filter(tkey = tkey).order_by('time');
    if len(toolInfos) > 0:
        # 获取工具基础信息
        baseInfo = toolInfos[0].tkey;
        result = {
            "hasTool" : True,
            "isCollected" : False,
            "baseInfo" : {
                "name" : baseInfo.name,
                "category" : baseInfo.category,
                "tkey" : baseInfo.tkey,
                "description" : baseInfo.description,
                "downloadCount" : baseInfo.download or 0,
                "score" : baseInfo.score or 0.0,
                "author" :  baseInfo.uid.name,
                "time" :  baseInfo.time,
            },
            "toolInfoList" : [],
            "commentInfoList" : [],
        };
        # 是否收藏了工具
        collections = models.Collection.objects.filter(uid = baseInfo.uid, tkey = tkey);
        if len(collections) > 0:
            result["isCollected"] = True;
        # 工具列表
        result["toolInfoList"].extend([{
            "version" : toolInfo.version,
            "IPVersion" : toolInfo.ip_version,
            "url" : toolInfo.file_path.url,
            "changelog" : toolInfo.changelog,
            "uploadTime" :  toolInfo.time,
        } for toolInfo in toolInfos]);
        # 评论信息
        commentInfos = baseInfo.comment_set.all();
        result["commentInfoList"].extend([{
            "user" : commentInfo.uid.name,
            "time" : commentInfo.time,
            "score" : commentInfo.score,
            "content" : commentInfo.content,
        } for commentInfo in commentInfos]);
    return result;
