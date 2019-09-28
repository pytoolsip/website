
from django.core.mail import send_mail
from DBModel import models
from website import settings

from _Global import _GG;

from enum import Enum;

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