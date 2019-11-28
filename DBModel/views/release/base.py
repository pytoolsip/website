
from django.core.cache import cache
import django.utils.timezone as timezone
from django.core.mail import send_mail
from DBModel import models
from website import settings

from _Global import _GG;

from enum import Enum;

# 上传状态穷举值
class ArticleType(Enum):
    Article = 0 # 文章
    Tool    = 1 # 工具详情

# 上传状态穷举值
class Status(Enum):
    Examing = 0   # 审核中
    Released = 1  # 已发布
    Withdrew = 2  # 已撤回

# 发送消息给所有管理员
def sendMsgToAllMgrs(msg):
    managers = models.UserAuthority.objects.filter(authority = 1); # 获取有管理员权限的用户
    mgrEmails = [manager.uid.email for manager in managers if manager.uid.email != settings.EMAIL_HOST_USER];
    return sendToEmails(msg, mgrEmails);

def sendToEmails(msg, emails):
    # 发送邮件给指定邮箱
    try:
        send_mail("PyToolsIP通知", msg, settings.EMAIL_HOST_USER, emails, fail_silently=False);
        return True;
    except Exception as e:
        _GG("Log").e("邮件发送失败!", e);
    return False;

def sendNotice(user, opUser, opType, msg, article = None):
    # 保存通知数据
    n = models.Notice(uid = user, opuid = opUser, optype = opType, content = msg, time = timezone.now(), aid = article);
    n.save();
    # 更新最新通知
    updateLatestNotice(n);
    # 发送通知
    appIdKey = f"pytoolsip_app_id_{user.id}";
    if cache.has_key(appIdKey):
        appId = cache.get(appIdKey);
        consumer = _GG("ConsumerMgr").getAppConsumer(appId);
        if consumer != None:
            result = {
                "noticeType": "ptip",
                "opUser": {
                    "name" : opUser.name,
                    "img" : opUser.img and opUser.img.url or "/pytoolsip/static/img/dzjh-icon.png",
                },
                "article": {},
                "tool": {},
                "content": msg,
            };
            if article:
                if article.atype == ArticleType.Tool.value:
                    result["noticeType"] = "tool";
                else:
                    result["noticeType"] = "article";
            consumer.notice();
    pass;

# 更新最新通知
def updateLatestNotice(notice):
    targetId = -1;
    if notice.aid:
        targetId = notice.aid.id;
    latestNotices = models.NoticeLatest.objects.filter(uid = notice.uid, tgid = targetId);
    if len(latestNotices) > 0:
        for latestNotice in latestNotices:
            latestNotice.latest_nid = notice;
            latestNotice.save();
    else:
        n = models.NoticeLatest(uid = notice.uid, tgid = targetId, latest_nid = notice, time = timezone.now());
        n.save();
    pass;