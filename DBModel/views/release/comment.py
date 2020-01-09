import django.utils.timezone as timezone;
from website import settings
from DBModel import models;

from _Global import _GG;

from release.base import *

# 审核评论
def examComment(request, userAuth, result, isSwitchTab):
    if not isSwitchTab and userAuth.authority == 1:
        examType, cid = request.POST.get("examType", None), request.POST.get("id", None);
        if examType and cid:
            try:
                c = models.Comment.objects.get(id = cid);
                if request.POST["examType"] == "delete":
                    c.delete();
                    result["requestTips"] = f"评论【{cid}, {c.uid.name}, {c.content}】删除成功。";
                    # 发送邮件通知
                    try:
                        sendMsgToAllMgrs(f"管理员【{userAuth.uid.name}】于{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}，成功【删除】评论【{cid}, {c.uid.name}, {c.content}】。");
                        exMsg = f"【删除原因：{request.POST.get('reason', '无。')}】";
                        sendToEmails(f"您在（{c.time.strftime('%Y-%m-%d %H:%M:%S')}）上传的评论【{cid}, {c.uid.name}, {c.content}】，于（{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}）成功删除。\n{exMsg}");
                    except Exception as e:
                        _GG("Log").e(f"Failed to send message to all managers! Error({e})!")
            except Exception as e:
                _GG("Log").e(f"Failed to examine online comment! Error({e})!")
                result["requestFailedTips"] = f"评论【{cid}, {c.uid.name}, {c.content}】审核失败！";
    # 返回线上评论
    infoList = models.Comment.objects.all().order_by('-time');
    result["onlineInfoList"] = [{
        "id" : info.id,
        "userName" : info.uid.name,
        "target" : info.aid.title + "【" + info.aid.sub_title + "】",
        "targetUrl" : getUrlByArticle(info.aid),
        "content" : info.content,
        "time" : info.time,
    } for info in infoList];

# 获取今日推荐
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