from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse

from DBModel import models

import hashlib;

# 平台键值列表
PtipKeyList = ["ptip_script", "ptip_exe", "update_exe"];
# 工具键值列表
PtKeyList = ["pt_new_script", "pt_ol_script"];

# 后台管理页请求
@csrf_exempt
def manage(request):
    print("manage get :", request.GET, "manage post :", request.POST, "manage files :", request.FILES);
    # 判断是否校验
    if "isVerify" in request.POST:
        return verify(request);
    # 判断是否已登陆
    if "uname" not in request.POST or "upwd" not in request.POST:
        return render(request, "manage/index.html");
    try:
        user = models.User.objects.get(name = request.POST["uname"], password = request.POST["upwd"]);
        if request.POST.get("isLogin", False):
            return JsonResponse({
                "isSuccess" : True,
                "name" : user.name,
                "pwd" : user.password,
            });
        if request.POST.get("isAfterLogin", False):
            return render(request, "manage/content.html", getManageResult(request, user, ""));
    except Exception as e:
        print(e);
        ret = {};
        if request.POST["uname"] and request.POST["upwd"]:
            ret = {"requestFailedTips" : "用户名和密码不匹配！"};
        return render(request, "manage/login.html", ret);
    # 获取请求键值
    mkey = request.POST.get("mk", "");
    # 判断是否重定向
    if (mkey not in PtipKeyList and mkey not in PtKeyList) or (mkey in PtipKeyList and user.authority == 0):
        # 重置mkey
        if user.authority == 0:
            mkey = PtKeyList[0];
        else:
            mkey = PtipKeyList[0];
    return render(request, "manage/content.html", getManageResult(request, user, mkey));

# 校验逻辑
def verify(request):
    # 校验工具名
    if "toolname" in request.POST:
        tkey = hashlib.md5(request.POST["toolname"].encode("utf-8")).hexdigest();
        if len(models.Tool.objects.filter(tkey = tkey)) == 0:
            return HttpResponse("true");
    # 校验失败
    print("Verify Fail!", request.POST);
    return HttpResponse("false");

# 获取管理页返回结果
def getManageResult(request, user, mkey):
    # 返回页面内容
    result = {
        "mkey" : mkey,
        "userInfo" : { # 用户信息
            "name":user.name,
            "pwd":user.password,
        },
        "isShowIpOption" : user.authority == 1, # 是否显示平台选项
        "requestTips" : "", # 请求提示
        "requestFailedTips" : "", # 请求失败提示
        "onlineInfoList" : [], # 线上信息列表
        "toolInfoData" : {"isUploadNew" : False, "isSearchNone" : False, "searchNoneTips" : ""}, # 工具信息数据
    };
    toolInfoData = result["toolInfoData"];
    if mkey == "ptip_script": # 更新平台脚本
        uploadPtipScript(request, user, result);
    elif mkey == "ptip_exe" or mkey == "update_exe": # 更新平台启动/更新程序
        uploadUpdateFile(request, user, mkey, result);
    elif mkey == "pt_new_script": # 上传新工具脚本
        uploadNewTool(request, user, result);
        toolInfoData["isUploadNew"] = True;
    elif mkey == "pt_ol_script": # 更新线上工具脚本
        tkey = request.POST.get("tkey", "");
        if tkey:
            # 返回线上版本数据
            toolInfoList = models.Tool.objects.filter(tkey = tkey, uid = user);
            if len(toolInfoList) > 0:
                # 从request.POST中获取上传数据
                uploadOlTool(request, user, tkey, result);
                # 返回线上版本数据
                result["onlineInfoList"] = getOnlineInfoList(toolInfoList[0]);
            else:
                toolInfoData["isSearchNone"] = True;
                toolInfoData["searchNoneTips"] = f"您未曾上传过ID为【{tkey}】工具，请重新搜索！";
        else:
            # 搜索工具信息数据
            result["toolInfoData"] = searchToolInfoData(request.POST.get("search", ""), user.id);
    return result;

# 校验分类
def _verifyCategory_(category, isAddSlash = True):
    category = category.replace(" ", "");
    if len(category) > 0:
        if isAddSlash and category[-1] != "/":
            category += "/";
        elif category[-1] == "/":
            category = category[:-1];
    return category;

# 获取md5码
def _getMd5_(name, category):
    name = _verifyCategory_(category) + name;
    return hashlib.md5(name.encode("utf-8")).hexdigest();

# 上传平台脚本
def uploadPtipScript(request, user, result):
    if "isSwitchTab" not in request.POST:
        if request.POST.get("version", None) and request.POST.get("file", None) and request.POST.get("changelog", None):
            version = request.POST["version"];
            p = models.Ptip(version = version, file_path = request.POST["file"], changelog = request.POST["changelog"], time = timezone.now());
            p.save();
            result["requestTips"] = f"PTIP平台脚本【{version}】上传成功。";
    # 返回线上版本数据
    ptipList = models.Ptip.objects.order_by('time');
    if len(ptipList) > 0:
        result["onlineInfoList"] = [{
            "version" : ptipInfo.version,
            "time" : ptipInfo.time,
            "changelog" : ptipInfo.changelog,
            "url" : ptipInfo.file_path.url,
        } for ptipInfo in ptipList];

# 上传更新文件
def uploadUpdateFile(request, user, name, result):
    if "isSwitchTab" not in request.POST:
        if "version" in request.POST and "file" in request.POST and "changelog" in request.POST:
            version = request.POST["version"];
            try:
                ud = models.Update.objects.get(name = name);
                ud.version = version;
                ud.file_path = request.POST["file"];
                ud.changelog = request.POST["changelog"];
                ud.time = timezone.now();
            except Exception as e:
                ud = models.Update(name = name, version = version, file_path = request.POST["file"], changelog = request.POST["changelog"], time = timezone.now());
            ud.save();
            result["requestTips"] = f"更新文件【{version}】上传成功。";
    # 返回线上版本数据
    updateList = models.Update.objects.filter(name = name).order_by('time');
    if len(updateList) > 0:
        result["onlineInfoList"] = [{
            "version" : updateInfo.version,
            "time" : updateInfo.time,
            "changelog" : updateInfo.changelog,
            "url" : updateInfo.file_path.url,
        } for updateInfo in updateList];

# 上传新工具
def uploadNewTool(request, user, result):
    if "isSwitchTab" not in request.POST:
        for k in ["name", "category", "file", "description", "version", "ip_version"]:
            if k not in request.POST:
                result["requestFailedTips"] = "上传信息不完整，请重新选上传！";
                return;
        version = request.POST["version"];
        try:
            tool = models.Tool.objects.get(name = name, category = category);
            result["requestFailedTips"] = "已存在相同分类的工具名，请重新选上传！";
            return;
        except Exception as e:
            name, category = request.POST["name"], _verifyCategory_(request.POST["category"], False);
            tkey = _getMd5_(name, category);
            curTime = timezone.now();
            # 保存Tool
            tool = models.Tool(uid = user, tkey = tkey, name = name, category = category, description = request.POST["description"], time = curTime);
            tool.save();
            # 保存ToolDetail
            toolDetail = models.ToolDetail(tkey = tool, version = version, ip_version = request.POST["ip_version"], file_path = request.POST["file"], changelog = "初始版本。", time = curTime);
            toolDetail.save();
        result["requestTips"] = f"新工具【{version}】上传成功。";

# 更新线上工具
def uploadOlTool(request, user, tkey, result):
    if "isSwitchTab" not in request.POST:
        for k in ["file", "description", "changelog", "version", "ip_version"]:
            if k not in request.POST:
                result["requestFailedTips"] = "上传信息不完整，请重新选上传！";
                return;
        version = request.POST["version"];
        try:
            tool = models.Tool.objects.get(tkey = tkey);
            curTime = timezone.now();
            # 更新Tool
            tool.description = request.POST["description"];
            tool.time = curTime;
            tool.save();
            # 保存ToolDetail
            toolDetail = models.ToolDetail(tkey = tool, version = version, ip_version = request.POST["ip_version"], file_path = request.POST["file"], changelog = request.POST["changelog"], time = curTime);
            toolDetail.save();
            result["requestTips"] = f"线上工具新版本【{version}】上传成功。";
        except Exception as e:
            print(e);

# 获取向上信息列表
def getOnlineInfoList(baseInfo):
    ptInfoList = models.ToolDetail.objects.filter(tkey = baseInfo.tkey).order_by('time');
    return [{
        "name" : baseInfo.name,
        "category" : baseInfo.category,
        "tkey" : baseInfo.tkey,
        "description" : baseInfo.description,
        "version" : ptInfo.version,
        "time" : ptInfo.time,
        "changelog" : ptInfo.changelog,
        "url" : ptInfo.file_path.url,
    } for ptInfo in ptInfoList];

# 搜索工具信息数据
def searchToolInfoData(toolName, uid):
    searchNoneTips = "";
    if toolName:
        toolInfoList = models.Tool.objects.filter(name__icontains = toolName, uid = uid);
        searchNoneTips = f"未搜索到名称为【{toolName}】的工具！";
    else:
        toolInfoList = models.Tool.objects.filter(uid = uid);
        searchNoneTips = f"您还未曾上传过工具到线上，请上传新工具！";
    return {
        "isSearchNone" : len(toolInfoList) == 0,
        "searchNoneTips" : searchNoneTips,
        "infoList" : [{
            "name" : toolInfo.name,
            "category" : toolInfo.category,
            "tkey" : toolInfo.tkey,
            "description" : toolInfo.description,
            "downloadCount" : toolInfo.download or 0,
            "score" : toolInfo.score or 0.0,
            "author" :  toolInfo.uid.name,
            "uploadTime" :  toolInfo.time,
        } for toolInfo in toolInfoList],
    };