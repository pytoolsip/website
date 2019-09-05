
from django.core.mail import send_mail
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
    managers = models.User.objects.filter(authority = 0);
    mgrEmails = [manager.email for manager in managers if manager.email != settings.EMAIL_HOST_USER];
    return sendToEmails(msg, mgrEmails);

def sendToEmails(msg, emails):
    # 发送邮件给指定邮箱
    try:
        send_mail("PyToolsIP通知", msg, settings.EMAIL_HOST_USER, emails, fail_silently=False);
        return True;
    except Exception as e:
        _GG("Log").e("邮件发送失败!", e);
    return False;