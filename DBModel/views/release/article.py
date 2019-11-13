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
        fields = ["title", "sub_title", "thumbnail", "content"]

# 上传状态穷举值
class ArticleType(Enum):
    Article = 0 # 文章
    Tool    = 1 # 工具详情

# 上传文章
def uploadArticle(request, userAuth, result, isSwitchTab):
    if not isSwitchTab:
        isRelease = base_util.getPostAsBool(request, "isRelease");
        if isRelease and "title" in request.POST:
            title, sub_title, thumbnail, content = request.POST["title"], request.POST.get("sub_title", None), request.FILES.get("thumbnail", None), request.POST.get("content", None);
            # a = models.Article(uid = userAuth.uid, title = file_path, sub_title = sub_title, thumbnail = thumbnail, content = content, time = timezone.now(), atype = ArticleType.Article.value, status = Status.Examing.value);
            # a.save();
            result["requestTips"] = f"文章【{title}】上传成功。";
        pass;
    result["articleType"] = ArticleType.Article.value;
    result["form"] = ArticleForm();

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
    # 返回需审核的文章
    articleList = models.Article.objects.filter(status = Status.Examing.value).order_by('-time');
    result["onlineInfoList"] = [{
            "id" : articleInfo.id,
            "title" : articleInfo.title,
            "time" : articleInfo.time,
        } for articleInfo in articleList];
    pass;

# 更新已发布文章
def updateOlArticle(request, userAuth, result, isSwitchTab):
    if not isSwitchTab:
        aid, opType = request.POST.get("aid", None), request.POST.get("opType", None);
        if aid and opType:
            try:
                a = models.Article.objects.get(id = request.POST["aid"]);
                if opType == "update" and a.atype == ArticleType.Tool.value:
                    result["isEdit"] = True;
                    result["articleType"] = a.atype;
                    result["form"] = ArticleForm(instance = a);
                    return;
                elif opType == "delete" and a.atype == ArticleType.Article.value:
                    a.delete();
                    result["requestTips"] = f"文章【{a.title}】成功删除。";
            except Exception as e:
                _GG("Log").w(e);
    # 返回需审核的文章
    searchText = request.POST.get("searchText", "");
    infoList = models.Article.objects.filter(title__icontains = searchText, uid = userAuth.uid, status = Status.Released.value).order_by('-time');
    result["searchText"] = searchText;
    result["isSearchNone"] = len(infoList) == 0;
    if not searchText:
        result["searchNoneTips"] = f"您未发布过文章~";
    else:
        result["searchNoneTips"] = f"您未发布过名称包含为【{searchText}】的文章，请重新搜索！";
    result["onlineInfoList"] = [{
            "id" : articleInfo.id,
            "title" : articleInfo.title,
            "subTitle" : articleInfo.sub_title,
            "thumbnail" : articleInfo.thumbnail,
            "content" : articleInfo.content,
            "time" : articleInfo.time,
            "author" : articleInfo.uid.name,
            "atype" : articleInfo.atype,
        } for articleInfo in infoList];
    pass;
