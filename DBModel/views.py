from django.shortcuts import render

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
