from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse

from DBModel import models

from DBModel import manage_view

# Create your views here.
# 首页
def home(request):
    # 平台信息列表
    ptipInfos = models.Ptip.objects.order_by('time');
    ptipInfoList = [{
            "version" : ptipInfo.version,
            "url" : ptipInfo.file_path.url,
            "changelog" : ptipInfo.changelog,
            "uploadTime" : ptipInfo.time,
            "downloadCount" : ptipInfo.download_count,
    } for ptipInfo in ptipInfos];
    # 工具信息列表
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
        "ptipInfoList" : ptipInfoList,
        "newestPtip" : ptipInfoList[-1],
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
    uid, t = -1, request.GET.get("t", "");
    # 收藏、评论处理
    if request.POST:
        # 保存uid
        uid = request.POST.get("uid", -1);
        try:
            user = models.User.objects.get(id = uid);
            tool = models.Tool.objects.get(tkey = t);
            # 保存收藏
            if "isCollect" in request.POST:
                collections = models.Collection.objects.filter(uid = uid, tkey = t);
                if request.POST["isCollect"] and len(collections) == 0:
                    c = models.Collection(uid = user, tkey = tool);
                    c.save();
                elif not request.POST["isCollect"] and len(collections) > 0:
                    collections.delete();
            # 保存评论
            isSave = True;
            for k in ["uid", "score", "content"]:
                if k not in request.POST:
                    isSave = False;
                    break;
            if isSave:
                c = models.Comment(uid = user, tkey = tool, score = request.POST["score"], content = request.POST["content"], time = timezone.now());
                c.save();
        except Exception as e:
            print(e);
    # 获取工具信息
    result = {"hasTool" : False};
    toolInfos = models.ToolDetail.objects.filter(tkey = t).order_by('time');
    if len(toolInfos) > 0:
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
        collections = models.Collection.objects.filter(uid = baseInfo.uid, tkey = t);
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

# 后台管理页
@csrf_exempt
def manage(request):
    print("manage get", request.GET)
    print("manage post", request.POST)
    if not request.POST or "uname" not in request.POST or "upwd" not in request.POST:
        return render(request, "login_manager.html", {"requestFailedTips" : "用户名或密码不能为空！"});
    try:
        user = models.User.objects.get(name = request.POST["uname"], password = request.POST["upwd"]);
        if request.POST.get("isLogin", False):
            return JsonResponse({
                "isSuccess" : True,
                "name" : user.name,
                "pwd" : user.password,
            });
    except Exception as e:
        print(e);
        return render(request, "login_manager.html", {"requestFailedTips" : "用户名和密码不匹配！"});
    print("user:::", user.name)
    # 网页键值跳转判断
    ptipKeyList, ptKeyList = manage_view.PtipKeyList, manage_view.PtKeyList;
    # 获取请求键值
    mkey = request.POST.get("mk", "");
    # 判断是否重定向
    if (mkey not in ptipKeyList and mkey not in ptKeyList) or (mkey in ptipKeyList and user.authority == 0):
        # 重置mkey
        if user.authority == 0:
            mkey = ptKeyList[0];
        else:
            mkey = ptipKeyList[0];
    return manage_view.manage(request, user, mkey);
