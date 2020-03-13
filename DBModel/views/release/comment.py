from django.db.models import Q;
import django.utils.timezone as timezone;
from website import settings;
from DBModel import models;

from _Global import _GG;

from release.base import *

# 审核评论
def examComment(request, userAuth, result, isSwitchTab):
    if not isSwitchTab and userAuth.authority == 1:
        examType, cid = request.POST.get("examType", None), request.POST.get("id", None);
        if examType and cid:
            try:
                c = models.Comment.objects.get(id = int(cid));
                if request.POST["examType"] == "delete":
                    c.delete();
                    result["requestTips"] = f"评论【{cid}, {c.uid.name}, {c.content}】删除成功。";
                    # 发送邮件通知
                    try:
                        sendMsgToAllMgrs(f"管理员【{userAuth.uid.name}】于{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}，成功【删除】评论【{cid}, {c.uid.name}, {c.content}】。");
                        exMsg = f"【删除原因：{request.POST.get('reason', '无。')}】";
                        sendToEmails(f"您在（{c.time.strftime('%Y-%m-%d %H:%M:%S')}）上传的评论【{cid}, {c.uid.name}, {c.content}】，于（{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}）成功删除。\n{exMsg}", [c.uid.email]);
                    except Exception as e:
                        _GG("Log").e(f"Failed to send message to all managers! Error({e})!")
            except Exception as e:
                _GG("Log").e(f"Failed to examine online comment! Error({e})!")
                result["requestFailedTips"] = f"评论【{cid}, {c.uid.name}, {c.content}】审核失败！";
    # 返回线上评论
    searchText = request.POST.get("searchText", "");
    infoList = models.Comment.objects.filter(content__icontains = searchText).order_by('-time');
    result["isSearchNone"] = len(infoList) == 0;
    result["searchText"] = searchText;
    if searchText:
        result["searchNoneTips"] = f"未搜索到内容包含【{searchText}】的评论，请重新搜索！";
    else:
        result["searchNoneTips"] = f"目前暂无已发布的评论！";
    result["onlineInfoList"] = [{
        "id" : info.id,
        "userName" : info.uid.name,
        "type" : info.aid.atype == ArticleType.Tool.value and "工具" or "文章",
        "target" : info.aid.title + "【" + info.aid.sub_title + "】",
        "targetUrl" : getUrlByArticle(info.aid),
        "content" : info.content,
        "time" : info.time,
    } for info in infoList];

# 获取文章路径
def getUrlByArticle(articleInfo):
    url = settings.HOME_URL + f"/article?aid={articleInfo.id}"
    if articleInfo.atype == ArticleType.Tool.value:
        tools = articleInfo.tool_set.all();
        if len(tools) > 0 :
            tkey = tools[0].tkey;
            url = settings.HOME_URL + f"/detail?t={tkey}";
        else:
            _GG("Log").w(f"Invalid tool's article[id={articleInfo.id}]!");
    return url;

# 评论开关
def switchComment(request, userAuth, result, isSwitchTab):
    if not isSwitchTab and userAuth.authority == 1:
        opType, aid = request.POST.get("opType", None), request.POST.get("aid", None);
        if opType == "allClose":
            cval = request.POST.get("isCloseAll", "false");
            cfg = models.Appconfig.objects.filter(ckey = "close_all_common");
            if len(cfg) == 0:
                cfg = models.Appconfig(ckey = "close_all_common", cval = cval);
            else:
                cfg = cfg[0];
                cfg.cval = cval;
            cfg.save();
            result["requestTips"] = f"网站配置【{cfg.ckey}】的值成功更新为【{cfg.cval}】。";
            # 发送邮件通知
            sendMsgToAllMgrs(f"管理员【{userAuth.uid.name}】于{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}，将网站配置【{cfg.ckey}】的值成功更新为【{cfg.cval}】");
        elif opType and aid:
            try:
                a = models.Article.objects.get(id = int(aid));
                targetState = "";
                if opType == "open":
                    a.comment_state = CommentType.Open.value;
                    targetState = "开启";
                elif opType == "close":
                    a.comment_state = CommentType.Close.value;
                    targetState = "关闭";
                if targetState:
                    a.save();
                    result["requestTips"] = f"【{aid}, {a.title}, {a.sub_title}】的评论功能成功{targetState}。";
                    # 发送邮件通知
                    sendMsgToAllMgrs(f"管理员【{userAuth.uid.name}】于{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}，成功【{targetState}】了【{aid}, {a.title}, {a.sub_title}】的评论功能。");
                    sendToEmails(f"您在（{a.time.strftime('%Y-%m-%d %H:%M:%S')}）发布的工具/文章【{aid}, {a.title}, {a.sub_title}】，于（{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}）成功{targetState}了评论功能。", [a.uid.email]);
                else:
                    result["requestFailedTips"] = f"提交的状态数据异常，【{aid}, {a.title}, {a.sub_title}】的评论功能开关切换失败！";
            except Exception as e:
                _GG("Log").e(f"Failed to operate the comment state of tool! Error({e})!")
                result["requestFailedTips"] = f"【{aid}, {a.title}, {a.sub_title}】的评论功能开关切换失败！";
    # 返回线上评论
    searchText = request.POST.get("searchText", "");
    infoList = models.Article.objects.filter(Q(title__icontains = searchText) | Q(sub_title__icontains = searchText)).order_by('-time');
    result["isSearchNone"] = len(infoList) == 0;
    result["searchText"] = searchText;
    if searchText:
        result["searchNoneTips"] = f"未搜索到标题/名称包含【{searchText}】的文章/工具，请重新搜索！";
    else:
        result["searchNoneTips"] = f"目前暂无已发布的文章/工具！";
    result["onlineInfoList"] = [{
        "id" : info.id,
        "userName" : info.uid.name,
        "type" : info.atype == ArticleType.Tool.value and "工具" or "文章",
        "target" : info.title + "【" + info.sub_title + "】",
        "targetUrl" : getUrlByArticle(info),
        "commentCount" : len(info.comment_set.all().order_by("-time")),
        "isClosed" : info.comment_state == CommentType.Close.value,
        "time" : info.time,
    } for info in infoList];
    # 更新所有关闭的选项
    cfg = models.Appconfig.objects.filter(ckey = "close_all_common");
    if len(cfg) > 0 and cfg[0].cval == "true":
        result["isAllClosed"] = True;
    pass;