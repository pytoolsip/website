from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse,HttpResponse
from django.core.mail import send_mail

from website import settings
from DBModel import models
from utils import base_util
import login;

from enum import Enum;
import hashlib;
import random;

# 平台键值列表
PtipKeyList = ["ptip_examination", "ptip_script", "ptip_exe", "update_exe", "depend_lib", "pt_ol_examination"];
# 工具键值列表
PtKeyList = ["pt_examination", "pt_new_script", "pt_ol_script"];

# 上传状态穷举值
class Status(Enum):
    Uploading = 0 # 上传中
    Examing = 1   # 审核中
    Released = 2  # 已发布
    Withdrew = 3  # 已撤回

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
    isSwitchTab = base_util.getPostAsBool(request, "isSwitchTab");
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
    if base_util.getPostAsBool(request, "isReqLogin"):
        return JsonResponse(login.getLoginInfo(uname, isReq = True));
    # 登陆时的返回数据
    if base_util.getPostAsBool(request, "isLogin"):
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
        "isManager" : user.authority == 1, # 是否显示平台选项
        "requestTips" : "", # 请求提示
        "requestFailedTips" : "", # 请求失败提示
        "onlineInfoList" : [], # 线上信息列表
    };
    if mkey == "ptip_examination": # 更新平台脚本
        examPtip(request, user, result, isSwitchTab);
    elif mkey == "ptip_script": # 更新平台脚本
        uploadPtipScript(request, user, result, isSwitchTab);
    elif mkey == "depend_lib": # 上传依赖库
        uploadDependLib(request, user, result, isSwitchTab);
    elif mkey == "ptip_exe" or mkey == "update_exe": # 更新平台启动/更新程序
        uploadExeFile(request, user, mkey, result, isSwitchTab);
    elif mkey == "pt_ol_examination": # 审核线上工具
        examOlTool(request, user, result, isSwitchTab);
    elif mkey == "pt_examination": # 审核工具
        examTool(request, user, result, isSwitchTab);
    elif mkey == "pt_new_script": # 上传新工具脚本
        uploadNewTool(request, user, result, isSwitchTab);
        result["isUploadNew"] = True;
    elif mkey == "pt_ol_script": # 更新线上工具脚本
        tkey = request.POST.get("tkey", "");
        if tkey:
            # 返回线上版本数据
            toolInfoList = models.Tool.objects.filter(tkey = tkey, uid = user);
            if len(toolInfoList) > 0:
                # 从request.POST中获取上传数据
                uploadOlTool(request, user, tkey, result, isSwitchTab);
                # 返回工具数据
                baseToolInfo = toolInfoList[0];
                result["onlineInfoList"] = getOnlineInfoList(baseToolInfo);
                result["baseToolInfo"] = {
                    "name" : baseToolInfo.name,
                    "category" : baseToolInfo.category,
                    "tkey" : baseToolInfo.tkey,
                    "description" : baseToolInfo.description,
                };
            else:
                result["isSearchNone"] = True;
                result["searchNoneTips"] = f"您未曾发布过ID为【{tkey}】工具，请重新搜索！";
        else:
            # 搜索工具信息数据
            searchToolInfoData(result, request.POST.get("searchType", ""), request.POST.get("searchText", ""), user.id);
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
            p = models.Ptip(version = version, file_path = request.FILES["file"], changelog = request.POST["changelog"], time = timezone.now(), project_path = pjFile, base_version = ".".join(vList[:1]), update_version = ".".join(vList[:1]), status = Status.Uploading.value);
            p.save();
            # 更新状态
            p.status = Status.Examing.value;
            p.save();
            result["requestTips"] = f"PTIP平台脚本【{version}】上传成功。";
        # 修改更新版本
        if "id" in request.POST and "updateVersion" in request.POST:
            if len(models.Ptip.objects.filter(status = Status.Released.value, base_version = request.POST["updateVersion"])) > 0:
                try:
                    p = models.Ptip.objects.get(id = request.POST["id"]);
                    p.update_version = request.POST["updateVersion"];
                    p.save();
                    result["requestTips"] = f"PTIP平台版本【{request.POST['updateVersion']}】更新成功。";
                except Exception as e:
                    print(e);
                    result["requestFailedTips"] = "所要更新版本的平台版本不存在，请刷新后重试！";
            else:
                result["requestFailedTips"] = "所选择的更新版本不存在，请重新选择！";
    # 返回线上版本数据
    ptipList = models.Ptip.objects.filter(status = Status.Released.value).order_by('time');
    ptipList = ptipList.values("base_version").distinct().order_by('base_version');
    if len(ptipList) > 0:
        baseVerList = [];
        for ptipInfo in ptipList:
            baseVerList.insert(0, ptipInfo.base_version);
            result["onlineInfoList"].append({
                "id" : ptipInfo.id,
                "version" : ptipInfo.version,
                "time" : ptipInfo.time,
                "changelog" : ptipInfo.changelog,
                "url" : ptipInfo.file_path.url,
                "update_version" : ptipInfo.update_version,
                "baseVerList" : baseVerList.copy(),
            });
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
            vList = version.split(".");
            exeDetail = models.ExeDetail(name = exe, version = version, file_path = request.FILES["file"], changelog = request.POST["changelog"], time = timezone.now(), base_version = ".".join(vList[:1]));
            exeDetail.save();
            result["requestTips"] = f"更新文件【{version}】上传成功。";
    # 返回线上版本数据
    try:
        exe = models.Exe.objects.get(name = name);
        exeList = models.exeDetail.objects.filter(name = exe).order_by('time');
        exeList = exeList.values("base_version").distinct();
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
            result["requestFailedTips"] = "上传信息不完整，请重新上传！";
            return;
        for k in ["name", "category", "description", "version", "ip_base_version"]:
            if k not in request.POST:
                result["requestFailedTips"] = "上传信息不完整，请重新上传！";
                return;
        version = request.POST["version"];
        try:
            tool = models.Tool.objects.get(name = name, category = category);
            result["requestFailedTips"] = "已存在相同分类的工具名，请重新上传！";
            return;
        except Exception as e:
            name, category = request.POST["name"], _verifyCategory_(request.POST["category"], False);
            tkey = _getMd5_(name, category);
            # 保存ToolExamination
            tool = models.ToolExamination(uid = user, tkey = tkey, name = name, category = category, description = request.POST["description"],
            version = version, ip_base_version = request.POST["ip_base_version"], file_path = request.FILES["file"], changelog = "初始版本。", time = timezone.now());
            tool.save();
        result["requestTips"] = f"新工具【{tkey}， {version}】上传成功。";
    result["olIPBaseVerList"] = getOlIPBaseVerList();

# 更新线上工具
def uploadOlTool(request, user, tkey, result, isSwitchTab):
    if not isSwitchTab:
        if "file" not in request.FILES:
            result["requestFailedTips"] = "上传信息不完整，请重新上传！";
            return;
        for k in ["description", "changelog", "version", "ip_base_version"]:
            if k not in request.POST:
                result["requestFailedTips"] = "上传信息不完整，请重新上传！";
                return;
        version = request.POST["version"];
        try:
            t = models.Tool.objects.get(tkey = tkey);
            # 保存ToolExamination
            tool = models.ToolExamination(uid = t.uid, tkey = t.tkey, name = t.name, category = t.category, description = request.POST["description"],
            version = version, ip_base_version = request.POST["ip_base_version"], file_path = request.FILES["file"], changelog = request.POST["changelog"], time = timezone.now());
            tool.save();
            result["requestTips"] = f"线上工具新版本【{t.tkey}， {version}】上传成功。";
        except Exception as e:
            print(e);
    result["olIPBaseVerList"] = getOlIPBaseVerList();

# 获取线上平台基础版本
def getOlIPBaseVerList():
    ptipList =  models.Ptip.objects.all().order_by('time');
    return ptipList.values("base_version").distinct();

# 获取线上信息列表
def getOnlineInfoList(baseInfo):
    ptInfoList = models.ToolDetail.objects.filter(tkey = baseInfo.tkey).order_by('time');
    ptInfoList = ptInfoList.values("base_version").distinct();
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
def searchToolInfoData(result, searchType, searchText, uid):
    searchNoneTips = "";
    if searchType == "name":
        toolInfoList = models.Tool.objects.filter(name__icontains = searchText, uid = uid);
        searchNoneTips = f"您未发布过名称包含为【{searchText}】工具，请重新搜索！";
    elif searchType == "tkey":
        toolInfoList = models.Tool.objects.filter(tkey = searchText, uid = uid);
        searchNoneTips = f"您未曾发布过ID为【{searchText}】工具，请重新搜索！";
    else:
        toolInfoList = models.Tool.objects.filter(uid = uid);
        searchNoneTips = f"您还未曾发布过工具到线上，请先上传新工具！";
    # 设置返回数据
    result["searchType"] = searchType;
    result["searchText"] = searchText;
    result["isSearchNone"] = len(toolInfoList) == 0;
    result["searchNoneTips"] = searchNoneTips;
    result["toolInfoList"] = [{
        "name" : toolInfo.name,
        "category" : toolInfo.category,
        "tkey" : toolInfo.tkey,
        "description" : toolInfo.description,
        "downloadCount" : toolInfo.download or 0,
        "score" : toolInfo.score or 0.0,
        "author" :  toolInfo.uid.name,
        "uploadTime" :  toolInfo.time,
    } for toolInfo in toolInfoList];

# 上传依赖库
def uploadDependLib(request, user, result, isSwitchTab):
    if not isSwitchTab:
        if "name" in request.POST and "file" in request.FILES and "description" in request.POST:
            name = request.POST["name"];
            try:
                models.Depend.objects.get(name = name);
                result["requestFailedTips"] =  f"已存在相同名称的依赖库【{name}】，请重新上传！";
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

# 审核平台
def examPtip(request, user, result, isSwitchTab):
    if not isSwitchTab and user.authority == 1:
        if "examType" in request.POST and "id" in request.FILES:
            pid = request.POST["id"];
            try:
                p, msg, reasonMsg = models.Ptip.objects.get(id = pid), "", "";
                if request.POST["examType"] == "release":
                    p.status = Status.Released.value;
                    msg = "发布";
                else:
                    p.delete();
                    msg, reasonMsg = "撤回", f"【撤回原因：{request.POST.get('reason', '无。')}】";
                result["requestTips"] = f"PTIP平台【{p.version}】成功{msg}。";
                # 发送邮件通知
                sendMsgToAllMgrs(f"管理员【{user.name}】于{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}，成功**{msg}**PTIP平台【{p.version}】。\n{reasonMsg}");
            except Exception as e:
                result["requestTips"] = f"平台【{p.version}】审核失败！";
    # 返回线上版本
    ptipList = models.Ptip.objects.filter(status = Status.Examing.value).order_by('time');
    if len(ptipList) > 0:
        result["onlineInfoList"] = [{
            "version" : ptipInfo.version,
            "time" : ptipInfo.time,
            "changelog" : ptipInfo.changelog,
            "url" : ptipInfo.file_path.url,
        } for ptipInfo in ptipList];

# 审核工具
def examTool(request, user, result, isSwitchTab):
    if not isSwitchTab:
        if "examType" in request.POST and "id" in request.POST:
            tid = request.POST["id"];
            try:
                t, msg, reasonMsg = models.ToolExamination.objects.get(id = tid), "", "";
                # 判断用户权限
                if user.authority == 0 and t.uid.id != user.id:
                    result["requestFailedTips"] = f"您没有权限审核工具【{t.tkey}，{t.version}】！";
                    return;
                if request.POST["examType"] == "release":
                    try:
                        tool = models.Tool.objects.get(name = t.name, category = t.category);
                        # 更新Tool
                        tool.description = t.description;
                        tool.time = t.time;
                        tool.save();
                    except Exception as e:
                        # 保存Tool
                        tool = models.Tool(uid = t.uid, tkey = t.tkey, name = t.name, category = t.category, description = t.description, time = t.time);
                        tool.save();
                    # 保存ToolDetail
                    toolDetail = models.ToolDetail(tkey = tool, version = t.version, ip_base_version = t.ip_base_version, file_path = t.file_path, changelog = t.changelog, time = t.time);
                    toolDetail.save();
                    msg = "发布";
                else:
                    t.delete();
                    msg, reasonMsg = "撤回", f"【撤回原因：{request.POST.get('reason', '无。')}】";
                result["requestTips"] = f"工具【{t.tkey}，{t.version}】成功{msg}。";
                # 发送邮件通知
                userIdentity, opMsg = "用户", "完成";
                if user.authority == 1:
                    userIdentity, opMsg = "管理员", "被管理员";
                sendMsgToAllMgrs(f"{userIdentity}【{user.name}】于{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}，成功**{msg}**工具【{t.tkey}，{t.version}】。");
                sendToEmails(f"您在{t.time.strftime('%Y-%m-%d %H:%M:%S')}上传的工具【{t.tkey}，{t.version}】，于{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}**{msg}**。\n{reasonMsg}", [t.uid.email]);
            except Exception as e:
                result["requestFailedTips"] = f"未找到工具【{t.tkey}，{t.version}】，审核失败！";
    # 返回线上版本
    toolList = models.ToolExamination.objects.all().order_by('time');
    if len(toolList) > 0:
        result["onlineInfoList"] = [{
            "id" : toolInfo.id,
            "name" : toolInfo.name,
            "category" : toolInfo.category,
            "tkey" : toolInfo.tkey,
            "description" : toolInfo.description,
            "version" : toolInfo.version,
            "time" : toolInfo.time,
            "changelog" : toolInfo.changelog,
            "url" : toolInfo.file_path.url,
        } for toolInfo in toolList];

# 审核线上工具
def examOlTool(request, user, result, isSwitchTab):
    if not isSwitchTab and user.authority == 1:
        if "examType" in request.POST and "id" in request.POST:
            tid = request.POST["id"];
            try:
                t = models.ToolDetail.objects.get(id = tid);
                if request.POST["examType"] == "delete":
                    t.delete();
                    if len(models.ToolDetail.objects.filter(tkey = t.tkey)) == 0:
                        t.tkey.delete();
                    result["requestTips"] = f"工具【{t.tkey}，{t.version}】下架成功。";
                    # 发送邮件通知
                    sendMsgToAllMgrs(f"管理员【{user.name}】于{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}，成功**下架**工具【{t.tkey}，{t.version}】。");
                    exMsg = f"【下架原因：{request.POST.get('reason', '无。')}】";
                    sendToEmails(f"您在{t.time.strftime('%Y-%m-%d %H:%M:%S')}上传的工具【{t.tkey}，{t.version}】，于{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}进行了**下架**。\n{exMsg}");
            except Exception as e:
                result["requestFailedTips"] = f"工具【{t.tkey}，{t.version}】审核失败！";
    # 设置权限
    result["isReleased"] = True;
    # 返回线上版本
    toolList = models.Tool.objects.all().order_by('time');
    for toolInfo in toolList:
        result["onlineInfoList"].extend(getOnlineInfoList(toolInfo));

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
        print("邮件发送失败!", e);
    return False;