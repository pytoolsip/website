import datetime
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse

from DBModel import models

# Create your views here.
# 首页
def home(request):
    toolInfoList = models.Tool.objects.order_by('time');
    return render(request, "home.html", {
        "toolInfoList" : [{
            "name" : toolInfo.name,
            "category" : toolInfo.category,
            "tkey" : toolInfo.tkey,
            "description" : toolInfo.description,
            "downloadCount" : toolInfo.download or 0,
            "score" : toolInfo.score or 0.0,
            "author" :  toolInfo.uid.name,
            "uploadTime" :  toolInfo.time,
        } for toolInfo in toolInfoList],
        "ptipInfoList" : [{
            "version" : "v1.0.0",
            "description" : "使用方式：下载后进行解压，双击PyToolsIP文件夹下的pytoolsip.exe，进行运行。\n注意：初次运行程序时，需要安装拉取模块，请保持网络能正常连接！",
            "uploadTime" : datetime(2019, 5, 11, 19, 37).timestamp(),
            "downloadCount" : 0,
            "url" : "http://jimdreamheart.club/release/pytoolsip/PyToolsIP-v1.0.0.zip",
        }],
    });

# 搜索页
def search(request):
    request.encoding = "utf-8";
    s = request.GET.get("s", "name");
    t = request.GET.get("t", "");
    result = {"isSearchNone" : False, "searchSelect" : s, "searchText" : t, "searchObject" : "工具", "toolInfoList" : [], "userInfoList" : []};
    # 校验提交的数据
    if not t:
        return render(request, "search.html", result);
    # 从数据库中查找数据
    if s == "id":
        toolInfos = models.Tool.objects.filter(tkey = t);
        if len(toolInfos) > 0:
            toolInfo = toolInfos[0];
            result["toolInfoList"].append({
                "name" : toolInfo.name,
                "category" : toolInfo.category,
                "tkey" : toolInfo.tkey,
                "description" : toolInfo.description,
                "downloadCount" : toolInfo.download or 0,
                "score" : toolInfo.score or 0.0,
                "author" :  toolInfo.uid.name,
                "uploadTime" :  toolInfo.time,
            });
    elif s == "author":
        if request.GET.get("q", "") == "tools":
            userInfos = models.User.objects.filter(name = t);
            if len(userInfos) > 0:
                toolInfoList = models.Tool.objects.filter(uid = userInfos[0].id);
                result["toolInfoList"].extend([{
                    "name" : toolInfo.name,
                    "category" : toolInfo.category,
                    "tkey" : toolInfo.tkey,
                    "description" : toolInfo.description,
                    "downloadCount" : toolInfo.download or 0,
                    "score" : toolInfo.score or 0.0,
                    "author" :  toolInfo.uid.name,
                    "uploadTime" :  toolInfo.time,
                } for toolInfo in toolInfoList]);
        else:
            userInfoList = models.User.objects.filter(name__icontains = t);
            result["userInfoList"].extend([{
                "name" : userInfo.name,
                "email" : userInfo.email,
            } for userInfo in userInfoList]);
            result["searchObject"] = "用户";
    else:
        toolInfoList = models.Tool.objects.filter(name__icontains = t);
        result["toolInfoList"].extend([{
            "name" : toolInfo.name,
            "category" : toolInfo.category,
            "tkey" : toolInfo.tkey,
            "description" : toolInfo.description,
            "downloadCount" : toolInfo.download or 0,
            "score" : toolInfo.score or 0.0,
            "author" :  toolInfo.uid.name,
            "uploadTime" :  toolInfo.time,
        } for toolInfo in toolInfoList]);
    # 判断是否搜索出了结果
    if len(result["toolInfoList"]) == 0 and len(result["userInfoList"]) == 0:
        result["isSearchNone"] = True;
    return render(request, "search.html", result);

# 工具详情页
@csrf_exempt
def detail(request):
    request.encoding = "utf-8";
    t = request.GET.get("t", "");
    # 保存评论内容
    if request.POST:
        isSave = True;
        for k in ["uid", "score", "content"]:
            if k not in request.POST:
                isSave = False;
                break;
        if isSave:
            try:
                user = models.User.objects.get(id = request.POST["uid"]);
                tool = models.Tool.objects.get(tkey = t);
                c = models.Comment(uid = user, tkey = tool, version = "1.0.0", score = request.POST["score"], content = request.POST["content"], time = timezone.now());
                c.save();
            except Exception as e:
                print(e);
    # 获取工具信息
    result = {"hasTool" : False};
    toolInfos = models.Tool.objects.filter(tkey = t);
    if len(toolInfos) > 0:
        toolInfo = toolInfos[0];
        result = {
            "hasTool" : True,
            "toolInfo" : {
                "name" : toolInfo.name,
                "category" : toolInfo.category,
                "tkey" : toolInfo.tkey,
                "description" : toolInfo.description,
                "downloadCount" : toolInfo.download or 0,
                "score" : toolInfo.score or 0.0,
                "author" :  toolInfo.uid.name,
                "uploadTime" :  toolInfo.time,
                "version" : toolInfo.version,
                "commonVersion" : toolInfo.common_version,
                "url" : toolInfo.url,
            },
            "commentInfoList" : [],
        };
        commentInfos = toolInfo.comment_set.all();
        result["commentInfoList"].extend([{
            "user" : commentInfo.uid.name,
            "time" : commentInfo.time,
            "score" : commentInfo.score,
            "content" : commentInfo.content,
        } for commentInfo in commentInfos]);
    return render(request, "detail.html", result);

# 登陆页
@csrf_exempt
def login(request):
    result = {"isSuccess" : False};
    if not request.POST:
        return JsonResponse(result);
    try:
        user = None;
        if "uid" in request.POST:
            user = models.User.objects.get(id = request.POST["uid"]);
        elif "name" in request.POST and "password" in request.POST:
            user = models.User.objects.get(name = request.POST["name"], password = request.POST["password"]);
        if user:
            result = {
                "isSuccess" : True,
                "uid" : user.id,
                "name" : user.name,
                "email" : user.email,
            };
    except Exception as e:
        print(e);
    return JsonResponse(result);