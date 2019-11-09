import django.utils.timezone as timezone;
from django.forms import CharField, ModelForm;
from DBModel import models;

from base import *;

from utils import base_util;

from _Global import _GG;

from base import *

# 文章表单
class ArticleForm(ModelForm):
    class Meta:
        model = models.Article
        fields = ["title", "thumbnail", "content"]

# 上传状态穷举值
class ArticleType(Enum):
    Article = 0 # 文章
    Tool    = 1 # 工具详情

# 上传文章
def uploadArticle(request, userAuth, result, isSwitchTab):
    pass;

# 上传工具详情文章
def uploadToolArticle(request, userAuth, result, isSwitchTab):
    pass;

# 审核文章
def examArticle(request, userAuth, result, isSwitchTab):
    if not isSwitchTab:
        examType, aid = request.POST.get("examType", None), request.POST.get("id", None);
        if examType and aid:
            try:
                a, msg, reasonMsg = models.Article.objects.get(id = aid), "", "";
                if a.status != Status.Examing.value:
                    result["requestFailedTips"] = f"文章【{t.title}】已进行过审核，此次审核失败！";
                    return;
                # 判断用户权限
                if userAuth.authority == 0 and a.uid.id != userAuth.uid.id:
                    result["requestFailedTips"] = f"您没有权限审核文章【{a.title}】！";
                    return;
                if examType == "release":
                    a.status = Status.Released.value;
                    a.save();
                    msg = "发布";
                else:
                    a.delete();
                    msg, reasonMsg = "撤回", f"【撤回原因：{request.POST.get('reason', '无。')}】";
                a.delete(); # 移除审核中的工具信息
                result["requestTips"] = f"文章【{a.title}】成功{msg}。";
                # 发送邮件通知
                userIdentity, opMsg = "用户", "完成";
                if userAuth.authority == 1:
                    userIdentity, opMsg = "管理员", "被管理员";
                sendMsgToAllMgrs(f"{userIdentity}【{userAuth.uid.name}】于{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}，成功**{msg}**文章【{a.title}】。");
                sendToEmails(f"您在（{a.time.strftime('%Y-%m-%d %H:%M:%S')}）上传的文章【{a.title}】，于（{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}）成功{msg}。\n{reasonMsg}", [a.uid.email]);
            except Exception as e:
                _GG("Log").w(e);
                result["requestFailedTips"] = f"未找到文章【{a.title}】，审核失败！";
    # 返回线上版本
    articleList = models.Article.objects.filter(status = Status.Examing.value).order_by('-time');
    result["onlineInfoList"] [{
            "id" : articleInfo.id,
            "title" : articleInfo.title,
            "time" : articleInfo.time,
            "url" : articleInfo.file_path.url,
        } for articleInfo in articleList];
    pass;

# 更新已发布文章
def updateOlArticle(request, userAuth, result, isSwitchTab):
    pass;
