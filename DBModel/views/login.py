from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse
from django.core.cache import cache

from DBModel import models
from utils import base_util, pwd_util

from _Global import _GG;

import hashlib;
import random;

# 登陆页请求
@csrf_exempt
def login(request):
    uname, upwd = request.POST.get("uname", ""), request.POST.get("upwd", "");
    _GG("Log").d("===== login =====", uname, upwd);
    return JsonResponse(getLoginInfo(uname, upwd = upwd, isReq = base_util.getPostAsBool(request, "isReqLogin"), isLogin = base_util.getPostAsBool(request, "isLogin"), isRemember = base_util.getPostAsBool(request, "isRemember")));

# 获取登录信息
def getLoginInfo(uname, upwd = "", isReq = False, isLogin = False, isRemember = False):
    result = {"isSuccess" : False};
    if isReq:
        if len(models.User.objects.filter(name = uname)) == 0:
            return {
                "isSuccess" : False,
                "tips" : "用户名不存在！",
            };
        # 返回编码密码函数
        code = pwd_util.getEncodeCode(); # 编码值
        _GG("Log").d("===== Login code =====", code);
        cache.set("|".join(["encode_pwd_code", "login", uname]), code, 2*60);
        return {
            "isSuccess" : True,
            "encodePwd" : pwd_util.getEncodePwdFunc(code),
        };
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
            randCode = "".join([str(i) for i in random.sample(range(10), 8)]); # 8位随机码
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
        pwd = upwd;
        verifyKey = "|".join(["encode_pwd_code", "login", uname]);
        if isLogin:
            if not cache.has_key(verifyKey):
                return {
                    "isSuccess" : False,
                    "tips" : "验证码已过期！",
                };
            pwd = pwd_util.decodePwd(upwd, int(cache.get(verifyKey)));
        elif cache.has_key(upwd):
            # 从缓存中读取密码
            pwd = cache.get(upwd);
        # 返回数据
        _GG("Log").d("===== Get Login User By ===== :", uname, pwd);
        return models.User.objects.get(name = uname, password = pwd);
    except Exception as e:
        _GG("Log").d(e);
    return None;