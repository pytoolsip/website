from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse

from DBModel import models
import login;

import hashlib;
import random;

# 平台键值列表
PtipKeyList = ["ptip_script", "ptip_exe", "update_exe", "depend_lib"];
# 工具键值列表
PtKeyList = ["pt_new_script", "pt_ol_script"];

# 后台管理页请求
@csrf_exempt
def manage(request):
    print("manage get :", request.GET, "manage post :", request.POST, "manage files :", request.FILES);
    # 判断是否校验
    if "isVerify" in request.POST:
        return verify(request);
    # 登陆平台
    loginInfo = loginIP(request);
    if loginInfo != None:
        return loginInfo;
    # 判断是否已登陆
    if "uname" not in request.POST or "upwd" not in request.POST:
        return render(request, "manage/index.html");
    # 获取登陆玩家
    user = login.getLoginUser(request.POST["uname"], request.POST["upwd"]);
    if not user:
        # 返回登陆页面信息
        ret = {};
        if request.POST["uname"] and request.POST["upwd"]:
            ret = {"requestFailedTips" : "登陆信息已过期！"};
        return render(request, "manage/login.html", ret);
    # 是否切换Tab
    isSwitchTab = request.POST.get("isSwitchTab", False);
    # 获取请求键值
    mkey = request.POST.get("mk", "");
    # 判断是否重定向
    if (mkey not in PtipKeyList and mkey not in PtKeyList) or (mkey in PtipKeyList and user.authority == 0):
        # 重置mkey
        if user.authority == 0:
            mkey = PtKeyList[0];
        else:
            mkey = PtipKeyList[0];
        isSwitchTab = True;
    # 返回管理项的内容
    return render(request, "manage/item.html", getManageResult(request, user, mkey, isSwitchTab));

# 登陆平台
def loginIP(request):
    # 判断是否请求登陆
    uname = request.POST.get("uname", "");
    if request.POST.get("isReqLogin", False):
        return JsonResponse(login.getLoginInfo(uname, isReq = True));
    # 登陆时的返回数据
    if request.POST.get("isLogin", False):
        loginInfo = login.getLoginInfo(uname, upwd = request.POST.get("upwd", ""), isLogin = True);
        if loginInfo.get("isSuccess", False):
            return JsonResponse(loginInfo);
        else:
            return render(request, "manage/login.html", {"requestFailedTips" : "用户名和密码不匹配！"});
    return None;

# 校验逻辑
def verify(request):
    # 校验工具名
    if "toolname" in request.POST:
        tkey = hashlib.md5(request.POST["toolname"].encode("utf-8")).hexdigest();
        if len(models.Tool.objects.filter(tkey = tkey)) == 0:
            return HttpResponse("true");
    # 校验依赖库名
    if "dependName" in request.POST:
        if len(models.Depend.objects.filter(name = request.POST["dependName"])) == 0:
            return HttpResponse("true");
    # 校验失败
    print("Verify Fail!", request.POST);
    return HttpResponse("false");

# 获取管理页返回结果
def getManageResult(request, user, mkey, isSwitchTab):
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
        uploadPtipScript(request, user, result, isSwitchTab);
    elif mkey == "depend_lib": # 上传依赖库
        uploadDependLib(request, user, result, isSwitchTab);
    elif mkey == "ptip_exe" or mkey == "update_exe": # 更新平台启动/更新程序
        uploadExeFile(request, user, mkey, result, isSwitchTab);
    elif mkey == "pt_new_script": # 上传新工具脚本
        uploadNewTool(request, user, result, isSwitchTab);
        toolInfoData["isUploadNew"] = True;
    elif mkey == "pt_ol_script": # 更新线上工具脚本
        tkey = request.POST.get("tkey", "");
        if tkey:
            # 返回线上版本数据
            toolInfoList = models.Tool.objects.filter(tkey = tkey, uid = user);
            if len(toolInfoList) > 0:
                # 从request.POST中获取上传数据
                uploadOlTool(request, user, tkey, result, isSwitchTab);
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
def uploadPtipScript(request, user, result, isSwitchTab):
    if not isSwitchTab:
        if request.POST.get("version", None) and request.FILES.get("file", None) and request.POST.get("changelog", None):
            # 合成工程文件
            pjFile = "";
            # 保存脚本文件
            version = request.POST["version"];
            vList = version.split(".");
            p = models.Ptip(version = version, file_path = request.FILES["file"], changelog = request.POST["changelog"], time = timezone.now(), project_path = pjFile, base_version = ".".join(vList[:1]), update_version = ".".join(vList[:1]));
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
    # 返回所依赖的线上版本
    for exe in models.Exe.objects.all():
        exeInfoList = models.ExeDetail.objects.filter(name = exe).order_by('time');
        if len(exeInfoList) > 0:
            result["onlineExeInfoList"].append({"name" : exe.name, "list" : [{
                "version" : exeInfo.version,
                "time" : exeInfo.time,
                "changelog" : exeInfo.changelog,
                "url" : exeInfo.file_path.url,
            } for exeInfo in exeInfoList]});

# 上传程序文件
def uploadExeFile(request, user, name, result, isSwitchTab):
    if not isSwitchTab:
        if "version" in request.POST and "file" in request.FILES and "changelog" in request.POST:
            try:
                exe = models.Exe.objects.get(name = name);
            except Exception as e:
                exe = models.Exe(name = name);
                exe.save();
            # 保存程序详情
            version = request.POST["version"];
            exeDetail = models.ExeDetail(name = exe, version = version, file_path = request.FILES["file"], changelog = request.POST["changelog"], time = timezone.now());
            exeDetail.save();
            result["requestTips"] = f"更新文件【{version}】上传成功。";
    # 返回线上版本数据
    try:
        exe = models.Exe.objects.get(name = name);
        exeList = models.exeDetail.objects.filter(name = exe).order_by('time');
        if len(exeList) > 0:
            result["onlineInfoList"] = [{
                "version" : updateInfo.version,
                "time" : updateInfo.time,
                "changelog" : updateInfo.changelog,
                "url" : updateInfo.file_path.url,
            } for updateInfo in exeList];
    except Exception as e:
        print(e);

# 上传新工具
def uploadNewTool(request, user, result, isSwitchTab):
    if not isSwitchTab:
        if "file" not in request.FILES:
            result["requestFailedTips"] = "上传信息不完整，请重新选上传！";
            return;
        for k in ["name", "category", "description", "version", "ip_version"]:
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
            ipVList = request.POST["ip_version"].split(".");
            toolDetail = models.ToolDetail(tkey = tool, version = version, ip_base_version = ipVList[:1], file_path = request.FILES["file"], changelog = "初始版本。", time = curTime);
            toolDetail.save();
        result["requestTips"] = f"新工具【{version}】上传成功。";

# 更新线上工具
def uploadOlTool(request, user, tkey, result, isSwitchTab):
    if not isSwitchTab:
        if "file" not in request.FILES:
            result["requestFailedTips"] = "上传信息不完整，请重新选上传！";
            return;
        for k in ["description", "changelog", "version", "ip_version"]:
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
            ipVList = request.POST["ip_version"].split(".");
            toolDetail = models.ToolDetail(tkey = tool, version = version, ip_base_version = ipVList[:1], file_path = request.FILES["file"], changelog = request.POST["changelog"], time = curTime);
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

# 上传依赖库
def uploadDependLib(request, user, result, isSwitchTab):
    if not isSwitchTab:
        if "name" in request.POST and "file" in request.FILES and "description" in request.POST:
            name = request.POST["name"];
            try:
                models.Depend.objects.get(name = name);
                result["requestFailedTips"] =  f"已存在相同名称的依赖库【{name}】，请重新选上传！";
            except Exception as e:
                depend = models.Depend(name = name, file_path = request.FILES["file"], description = request.POST["description"], time = timezone.now());
                depend.save();
                result["requestTips"] = f"上传依赖库【{name}】上传成功。";
    # 返回线上版本数
    dependList = models.Depend.objects.filter(name = request.POST.get("name", "")).order_by('time');
    if len(dependList) > 0:
        result["onlineInfoList"] = [{
            "name" : dependInfo.name,
            "time" : dependInfo.time,
            "description" : dependInfo.description,
            "url" : dependInfo.file_path.url,
        } for dependInfo in dependList];
