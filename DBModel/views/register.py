from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse,HttpResponse
from django.core.cache import cache
from django.core.mail import send_mail

from website import settings
from DBModel import models
from utils import base_util, pwd_util, random_util

from _Global import _GG;

import random;

# 注册请求
@csrf_exempt
def register(request):
    _GG("Log").i("register get :", request.GET, "; register post :", request.POST, "; register files :", request.FILES);
    # 判断是否校验
    if base_util.getPostAsBool(request, "isVerify"):
        return verify(request);
    # 获取验证码
    if base_util.getPostAsBool(request, "isGetVerifyCode"):
        return getVerifyCode(request);
    # 注册用户
    if base_util.getPostAsBool(request, "isRegister"):
        return registerUser(request);
    # 重置用户密码
    if base_util.getPostAsBool(request, "isResetPwd"):
        return resetUserPwd(request);
    return HttpResponse("");

# 校验逻辑
def verify(request):
    # 校验用户名
    if "uname" in request.POST:
        if len(models.User.objects.filter(name = request.POST["uname"])) == 0:
            return HttpResponse("true");
    # 校验邮箱
    if "email" in request.POST:
        isExist = len(models.User.objects.filter(email = request.POST["email"])) > 0;
        if isExist == base_util.getPostAsBool(request, "isExist"):
            return HttpResponse("true");
    # 校验失败
    _GG("Log").d("Verify Fail!", request.POST);
    return HttpResponse("false");

# 获取验证码
def getVerifyCode(request):
    email = request.POST.get("email", "");
    if not email:
        return JsonResponse({"isSuccess" : False, "tips" : "邮箱信息不能为空！"});
    # 生成8位随机验证码
    verifyCode = random_util.randomNum(6); # 6位随机码
    # 发送邮件给指定邮箱
    try:
        send_mail("PyToolsIP", "平台验证码："+verifyCode, settings.EMAIL_HOST_USER, [email], fail_silently=False);
    except Exception as e:
        _GG("Log").d(e);
        return JsonResponse({"isSuccess" : False, "tips" : "验证码发送失败，请检查邮箱是否正确！"});
    # 缓存验证码
    expires = 2*60; # 缓存2分钟
    cache.set("|".join(["verify_code", "register", email]), verifyCode, expires);
    return JsonResponse({"isSuccess" : True, "expires" : expires});

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
    # 保存用户信息
    pwd = _GG("DecodeStr")(upwd);
    salt = random_util.randomMulti(32);
    password = pwd_util.encodePassword(salt, pwd);
    models.User(name = uname, password = password, salt = salt, email = email, authority = 0).save();
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
    # 更新密码及salt值
    pwd = _GG("DecodeStr")(upwd);
    user.salt = random_util.randomMulti(32);
    user.password = pwd_util.encodePassword(salt, pwd);
    user.save();
    return JsonResponse({"isSuccess" : True});
