from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse
from django.core.cache import cache

from DBModel import models
from utils import base_util, pwd_util, random_util

from _Global import _GG;

import hashlib;
import random;

# 登陆页请求
@csrf_exempt
def login(request):
    uname, upwd = request.POST.get("uname", ""), request.POST.get("upwd", "");
    _GG("Log").d("===== login =====", uname, upwd);
    return JsonResponse(getLoginInfo(uname, upwd = upwd, isLogin = base_util.getPostAsBool(request, "isLogin"), isRemember = base_util.getPostAsBool(request, "isRemember")));

# 获取登录信息
def getLoginInfo(uname, upwd = "", isLogin = False, isRemember = False):
    result = {"isSuccess" : False};
    # 获取登陆玩家
    user = getLoginUser(uname, upwd, isLogin);
    if user:
        result = {
            "isSuccess" : True,
            "name" : user.name,
            "email" : user.email,
        };
        # 缓存玩家密码对应的md5
        if isLogin:
            randCode = random_util.randomNum(8); # 8位随机码
            result["pwd"] = hashlib.md5("|".join([user.password, randCode]).encode("utf-8")).hexdigest();
            result["expires"] = 12*60*60; # 默认12小时
            if isRemember:
                result["expires"] = 10*24*60*60; # 10天
            # 缓存密码信息
            cache.set(result["pwd"], user.password, result["expires"]);
            pwdKey = "|".join(["password", user.name, user.password]);
            if cache.has_key(pwdKey) and cache.has_key(cache.get(pwdKey)):
                cache.delete(cache.get(pwdKey));
            cache.set(pwdKey, result["pwd"], result["expires"]);
    else:
        result["tips"] = "用户名和密码不匹配！";
    return result;

# 获取登陆玩家
def getLoginUser(uname, upwd, isLogin = False):
    try:
        pwd = _GG("DecodeStr")(upwd);
        if isLogin:
            user = models.User.objects.get(name = uname);
            pwd = pwd_util.encodePassword(user.salt, pwd);
        elif cache.has_key(pwd):
            # 从缓存中读取密码
            pwd = cache.get(pwd);
        # 返回数据
        _GG("Log").d("===== Get Login User By ===== :", uname, pwd);
        return models.User.objects.get(name = uname, password = pwd);
    except Exception as e:
        _GG("Log").d(e);
    return None;