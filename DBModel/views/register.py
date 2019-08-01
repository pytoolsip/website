from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse
from django.core.cache import cache

from DBModel import models

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
    # 注册用户
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
    models.User(name = uname, password = upwd, email = email, authority = 0).save();
    return JsonResponse({"isSuccess" : True});

# 校验逻辑
def verify(request):
    # 校验用户名
    if "uname" in request.POST:
        if len(models.User.objects.filter(name = request.POST["uname"])) == 0:
            return HttpResponse("true");
    # 校验邮箱
    if "email" in request.POST:
        if len(models.User.objects.filter(email = request.POST["email"])) == 0:
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

