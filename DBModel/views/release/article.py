import django.utils.timezone as timezone;
from django.forms import CharField, ModelForm;
from django.forms.widgets import HiddenInput;
from DBModel import models;

from release.base import *;

from utils import base_util;

from _Global import _GG;

# 文章表单
class ArticleForm(ModelForm):
    class Meta:
        model = models.ArticleExamination
        fields = ["title", "sub_title", "thumbnail", "content", "sketch"]

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs);
        self.fields["sketch"].widget = HiddenInput();

# 上传文章
def uploadArticle(request, userAuth, result, isSwitchTab):
    if not isSwitchTab:
        isRelease = base_util.getPostAsBool(request, "isRelease");
        if isRelease:
            af = ArticleForm(request.POST, request.FILES);
            if af.is_valid():
                ae = models.ArticleExamination(**{
                    "uid" : userAuth.uid,
                    "title" : af.cleaned_data["title"],
                    "sub_title" : af.cleaned_data.get("sub_title", None),
                    "thumbnail" : af.cleaned_data.get("thumbnail", None),
                    "sketch" : af.cleaned_data["sketch"],
                    "content" : af.cleaned_data["content"],
                    "time" : timezone.now(),
                    "atype" : ArticleType.Article.value,
                });
                ae.save();
                result["requestTips"] = f"文章【{ae.title}】上传成功，正在等待审核。";
        pass;
    result["articleType"] = ArticleType.Article.value;
    result["form"] = ArticleForm();

# 审核文章
def examArticle(request, userAuth, result, isSwitchTab):
    if not isSwitchTab:
        examType, aid = request.POST.get("examType", None), int(request.POST.get("id", None));
        if examType and aid:
            try:
                ae, msg, reasonMsg = models.ArticleExamination.objects.get(id = aid), "", "";
                # 判断用户权限
                if userAuth.authority == 0 and ae.uid.id != userAuth.uid.id:
                    result["requestFailedTips"] = f"您没有权限审核文章【{ae.title}】！";
                    return;
                if examType == "release":
                    if ae.atype == ArticleType.Tool.value:
                        # 更新工具详情的数据
                        tl = models.Tool.objects.filter(name = ae.title, category = ae.sub_title);
                        if len(tl) == 0:
                            _GG("Log").d(f"所工具详情【{ae.title}[{ae.sub_title}]】没有对应的工具，发布失败！");
                            ae.thumbnail.delete();
                            ae.delete();
                        for t in tl:
                            # 保存工具详情
                            t.aid.thumbnail = ae.thumbnail;
                            t.aid.time = ae.time;
                            t.aid.save();
                            # 保存工具详情内容
                            t.aid.cid.content = ae.content;
                            t.aid.cid.save();
                    else:
                        # 新增文章
                        ac = models.ArticleContent(content = ae.content);
                        ac.save();
                        a = models.Article(**{
                            "uid" : ae.uid,
                            "title" : ae.title,
                            "sub_title" : ae.sub_title,
                            "thumbnail" : ae.thumbnail,
                            "sketch" : ae.sketch,
                            "cid" : ac,
                            "time" : ae.time,
                            "atype" : ae.atype,
                        });
                        a.save();
                    msg = "发布";
                else:
                    msg, reasonMsg = "撤回", f"【撤回原因：{request.POST.get('reason', '无。')}】";
                ae.delete();
                result["requestTips"] = f"文章【{ae.title}】成功{msg}。";
                # 发送邮件通知
                userIdentity, opMsg = "用户", "完成";
                if userAuth.authority == 1:
                    userIdentity, opMsg = "管理员", "被管理员";
                sendMsgToAllMgrs(f"{userIdentity}【{userAuth.uid.name}】于{timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S')}，成功**{msg}**文章【{ae.title}】。");
                sendToEmails(f"您在（{ae.time.strftime('%Y-%m-%d %H:%M:%S')}）上传的文章【{ae.title}】，于（{timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S')}）成功{msg}。\n{reasonMsg}", [ae.uid.email]);
            except Exception as e:
                _GG("Log").w(e);
                result["requestFailedTips"] = f"未找到文章【{aid}】，审核失败！";
    # 返回需审核的文章
    articleList = models.ArticleExamination.objects.all().order_by('-time');
    result["onlineInfoList"] = [{
            "id" : articleInfo.id,
            "title" : articleInfo.title,
            "subTitle" : articleInfo.sub_title or "",
            "sketch" : articleInfo.sketch,
            "time" : articleInfo.time,
        } for articleInfo in articleList];
    pass;

# 更新已发布文章
def updateOlArticle(request, userAuth, result, isSwitchTab):
    if not isSwitchTab:
        aid = request.POST.get("aid", None);
        if aid:
            try:
                a = models.Article.objects.get(id = aid);
                isRelease = base_util.getPostAsBool(request, "isRelease");
                if isRelease and a.atype == ArticleType.Tool.value:
                    af = ArticleForm(request.POST, request.FILES);
                    if af.is_valid():
                        ae = models.ArticleExamination(**{
                            "uid" : userAuth.uid,
                            "title" : a.title,
                            "sub_title" : a.sub_title,
                            "thumbnail" : af.cleaned_data.get("thumbnail", None),
                            "sketch" : af.cleaned_data["sketch"],
                            "content" : af.cleaned_data["content"],
                            "time" : timezone.now(),
                            "atype" : a.atype,
                        });
                        ae.save();
                        result["requestTips"] = f"工具详情【{a.title}[{a.sub_title}]】更新成功，正在等待审核。";
                opType = request.POST.get("opType", None);
                if opType:
                    if opType == "update" and a.atype == ArticleType.Tool.value:
                        result["isEdit"] = True;
                        result["articleType"] = a.atype;
                        result["form"] = ArticleForm(instance = models.ArticleExamination(**{
                            "uid" : a.uid,
                            "title" : a.title,
                            "sub_title" : a.sub_title,
                            "thumbnail" : a.thumbnail,
                            "content" : a.cid.content,
                        }));
                        result["aid"] = aid;
                        return;
                    elif opType == "delete" and a.atype == ArticleType.Article.value:
                        a.delete();
                        result["requestTips"] = f"文章【{a.title}】成功删除。";
            except Exception as e:
                _GG("Log").w(e);
    # 返回已发布的文章
    searchText = request.POST.get("searchText", "");
    infoList = models.Article.objects.filter(title__icontains = searchText, uid = userAuth.uid).order_by('-time');
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
            "thumbnail" : articleInfo.thumbnail and articleInfo.thumbnail.url or "",
            "sketch" : articleInfo.sketch,
            "time" : articleInfo.time,
            "author" : articleInfo.uid.name,
            "atype" : articleInfo.atype,
        } for articleInfo in infoList];
    pass;
