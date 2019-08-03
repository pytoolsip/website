from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse,HttpResponse
from django.core.cache import cache

from DBModel import models
import login;

import random;

# 注册请求
@csrf_exempt
def register(request):
    print("register get :", request.GET, "; register post :", request.POST, "; register files :", request.FILES);
    # 判断是否校验
    if request.POST.get("isVerify", False):
        return verify(request);
    # 获取验证码
    if request.POST.get("isGetVerifyCode", False):
        return getVerifyCode(request);
    # 请求编码方法
    if request.POST.get("isReq", False):
        return getEncodePwdInfo(request);
    # 注册用户
    if request.POST.get("isRegister", False):
        return registerUser(request);
    # 重置用户密码
    if request.POST.get("isResetPwd", False):
        return resetUserPwd(request);

# 校验逻辑
def verify(request):
    # 校验用户名
    if "uname" in request.POST:
        if len(models.User.objects.filter(name = request.POST["uname"])) == 0:
            return HttpResponse("true");
    # 校验邮箱
    if "email" in request.POST:
        isExist = len(models.User.objects.filter(email = request.POST["email"])) > 0;
        if isExist == request.POST.get("isExist", False):
            return HttpResponse("true");
    # 校验失败
    print("Verify Fail!", request.POST);
    return HttpResponse("false");

# 获取验证码
def getVerifyCode(request):
    email = request.POST.get("email", "");
    if not email:
        return JsonResponse({"isSuccess" : False, "tips" : "邮箱信息不能为空！"});
    # 生成8位随机验证码
    verifyCode = "".join([str(i) for i in random.sample(range(10), 8)]);
    ### 发送邮件给指定邮箱，注意得确认是否发送成功
    # 缓存验证码
    expires = 2*60; # 缓存2分钟
    cache.set("|".join(["verify_code", "register", email]), verifyCode, expires);
    return JsonResponse({"isSuccess" : True, "expires" : expires});

# 获取编码密码信息
def getEncodePwdInfo(request):
    email = request.POST.get("email", "");
    if not email:
        return {
            "isSuccess" : False,
            "tips" : "邮箱不能为空！",
        };
    # 返回编码密码函数
    code = "".join([str(random.randint(1,9)), str(random.randint(1,9))]); # 编码值
    print("===== Register code =====", code);
    cache.set("|".join(["encode_pwd_code", "register", email]), code, 2*60);
    return {
        "isSuccess" : True,
        "encodePwd" : login.getEncodePwdFunc(code),
    };

# 注册玩家
def registerUser(request):
    uname, upwd = request.POST.get("uname", ""), request.POST.get("upwd", "");
    email, verifyCode = request.POST.get("email", ""), request.POST.get("verifyCode", "");
    # 校验用户名
    if len(models.User.objects.filter(name = uname)) > 0:
        return JsonResponse({"isSuccess" : False, "tips" : "已存在相同用户名！"});
    # 校验邮箱
    if len(models.User.objects.filter(email = email)) > 0:
        return JsonResponse({"isSuccess" : False, "tips" : "邮箱已被注册！"});
    # 校验验证码
    if cache.get("|".join(["verify_code", "register", email])) != verifyCode:
        return JsonResponse({"isSuccess" : False, "tips" : "验证码不正确！"});
    # 保存用户数据
    verifyKey = "|".join(["encode_pwd_code", "register", email]);
    if not cache.has_key(verifyKey):
        return {
            "isSuccess" : False,
            "tips" : "验证码已过期！",
        };
    pwd = login.decodePwd(upwd, int(cache.get(verifyKey)));
    models.User(name = uname, password = pwd, email = email, authority = 0).save();
    return JsonResponse({"isSuccess" : True});

# 重置用户密码
def resetUserPwd(request):
    upwd = request.POST.get("upwd", "");
    email, verifyCode = request.POST.get("email", ""), request.POST.get("verifyCode", "");
    # 校验邮箱
    if len(models.User.objects.filter(email = email)) == 0:
        return JsonResponse({"isSuccess" : False, "tips" : "邮箱未注册！"});
    # 校验验证码
    if cache.get("|".join(["verify_code", "register", email])) != verifyCode:
        return JsonResponse({"isSuccess" : False, "tips" : "验证码不正确！"});
    # 根据邮箱获取用户
    try:
        user = models.User.objects.get(email = email);
    except Exception as e:
        return JsonResponse({"isSuccess" : True, "tips" : "用户邮箱异常！"});
    # 更新用户密码
    verifyKey = "|".join(["encode_pwd_code", "register", email]);
    if not cache.has_key(verifyKey):
        return {
            "isSuccess" : False,
            "tips" : "验证码已过期！",
        };
    user.password = login.decodePwd(upwd, int(cache.get(verifyKey)));
    user.save();
    return JsonResponse({"isSuccess" : True});
