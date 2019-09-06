from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from django.core.mail import send_mail
from website import settings
from DBModel import models
from utils import base_util
import userinfo;

import hashlib;
import os,sys;

from _Global import _GG;

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__));
sys.path.append(CURRENT_PATH);

try:
    import ptip;
    import depend;
    import tool;
    import installer;
except Exception as e:
	raise e;
finally:
	sys.path.remove(CURRENT_PATH);

# 平台键值列表
PtipKeyList = ["ptip_examination", "ptip_script", "ptip_installer", "ptip_exe", "depend_lib", "pt_ol_examination"];
# 工具键值列表
PtKeyList = ["pt_examination", "pt_new_script", "pt_ol_script"];

# 后台管理页请求
@csrf_exempt
def release(request):
    _GG("Log").d("release get :", request.GET, "release post :", request.POST, "release files :", request.FILES);
    # 判断是否校验
    if "isVerify" in request.POST:
        return verify(request);
    # 登陆平台
    loginInfo = loginIP(request);
    if loginInfo != None:
        return loginInfo;
    # 判断是否已登陆
    if "uname" not in request.POST or "upwd" not in request.POST:
        return render(request, "release/index.html", {"HOME_URL": settings.HOME_URL});
    # 获取登陆玩家
    user = userinfo.getLoginUser(request.POST["uname"], request.POST["upwd"]);
    if not user:
        # 返回登陆页面信息
        ret = {"HOME_URL": settings.HOME_URL};
        if request.POST["uname"] and request.POST["upwd"]:
            ret = {"requestFailedTips" : "登陆信息已过期！"};
        return render(request, "release/login.html", ret);
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
    return render(request, "release/item.html", getReleaseResult(request, user, mkey, isSwitchTab));

# 登陆平台
def loginIP(request):
    # 判断是否请求登陆
    if base_util.getPostAsBool(request, "isLogin"):
        loginInfo = userinfo.getLoginInfo(request.POST.get("uname", ""), upwd = request.POST.get("upwd", ""), isLogin = True);
        return JsonResponse(loginInfo);
    return None;

# 校验逻辑
def verify(request):
    # 校验工具名
    if "toolname" in request.POST:
        tkey = hashlib.md5(request.POST["toolname"].encode("utf-8")).hexdigest();
        if len(models.Tool.objects.filter(tkey = tkey)) + len(models.ToolExamination.objects.filter(tkey = tkey)) == 0:
            return HttpResponse("true");
    # 校验依赖库名
    if "exeName" in request.POST:
        if len(models.Exe.objects.filter(name = request.POST["exeName"])) == 0:
            return HttpResponse("true");
    # 校验依赖库名
    if "dependName" in request.POST:
        if len(models.Depend.objects.filter(name = request.POST["dependName"])) == 0:
            return HttpResponse("true");
    # 校验失败
    _GG("Log").d("Verify Fail!", request.POST);
    return HttpResponse("false");

# 获取管理页返回结果
def getReleaseResult(request, user, mkey, isSwitchTab):
    # 返回页面内容
    result = {
        "HOME_URL": settings.HOME_URL,
        "mkey" : mkey,
        "userInfo" : { # 用户信息
            "name":user.name,
            "email":user.email,
        },
        "isManager" : user.authority == 1, # 是否显示平台选项
        "requestTips" : "", # 请求提示
        "requestFailedTips" : "", # 请求失败提示
        "onlineInfoList" : [], # 线上信息列表
    };
    if mkey == "ptip_examination": # 更新平台脚本
        ptip.examine(request, user, result, isSwitchTab);
    elif mkey == "ptip_script": # 更新平台脚本
        ptip.upload(request, user, result, isSwitchTab);
    elif mkey == "ptip_installer": # 更新平台安装程序
        installer.uploadInstaller(request, user, result, isSwitchTab);
    elif mkey == "depend_lib": # 上传依赖库
        depend.uploadDepend(request, user, result, isSwitchTab);
    elif mkey == "ptip_exe": # 更新平台启动/更新程序
        depend.uploadExe(request, user, result, isSwitchTab);
    elif mkey == "pt_ol_examination": # 审核线上工具
        tool.examOlTool(request, user, result, isSwitchTab);
    elif mkey == "pt_examination": # 审核工具
        tool.examTool(request, user, result, isSwitchTab);
    elif mkey == "pt_new_script": # 上传新工具脚本
        tool.uploadNew(request, user, result, isSwitchTab);
    elif mkey == "pt_ol_script": # 更新线上工具脚本
        tkey = request.POST.get("tkey", "");
        if tkey:
            tool.uploadOl(request, user, tkey, result, isSwitchTab)
        else:
            # 搜索工具信息数据
            tool.searchTool(result, request.POST.get("searchType", ""), request.POST.get("searchText", ""), user.id);
    return result;
