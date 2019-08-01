from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse
from django.core.cache import cache

from DBModel import models

import hashlib;
import random;
import math;

# 登陆页请求
@csrf_exempt
def login(request):
    uname, upwd = request.POST.get("uname", ""), request.POST.get("upwd", "");
    print("===== login =====", uname, upwd);
    return JsonResponse(getLoginInfo(uname, upwd = upwd, isReq = request.POST.get("isReqLogin", False), isLogin = request.POST.get("isLogin", False), isRemember = request.POST.get("isRemember", False)));

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
        code = "".join([str(random.randint(1,9)), str(random.randint(1,9))]); # 编码值
        print("===== Login code =====", code);
        cache.set("|".join(["verify_code", "login", uname]), code, 2*60);
        return {
            "isSuccess" : True,
            "encodePwd" : getEncodePwdFunc(code),
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
            cache.set(result["pwd"], user.password, result["expires"]);
    else:
        result["tips"] = "用户名和密码不匹配！";
    return result;

# 获取登陆玩家
def getLoginUser(uname, upwd, isLogin = False):
    try:
        pwd = upwd;
        verifyKey = "|".join(["verify_code", "login", uname]);
        if isLogin:
            if not cache.has_key(verifyKey):
                return {
                    "isSuccess" : False,
                    "tips" : "验证码已过期！",
                };
            pwd = decodePwd(upwd, int(cache.get(verifyKey)));
        elif cache.has_key(upwd):
            # 从缓存中读取密码
            pwd = cache.get(upwd);
        # 返回数据
        print("===== Get Login User By ===== :", uname, pwd);
        return models.User.objects.get(name = uname, password = pwd);
    except Exception as e:
        print(e);
    return None;


# 获取编码密码函数
def getEncodePwdFunc(code):
    return """(function(pwd, code){
            var pwds = [];
            var space = Math.floor(code/10) + 1;
            var increment = code%10 + 1;
            for (var i = 0; i < pwd.length; i ++) {
                var col = Math.floor(i/space);
                var row = i%space * (Math.floor((pwd.length)/space) + 1);
                pwds.push(String.fromCharCode(pwd.charCodeAt(row + col) + increment));
                increment++;
            }
            return pwds.join("");
        })('$1', """+code+")";

# 解码登陆密码
def decodePwd(pwd, code):
    pwds = [""] * len(pwd);
    space, increment = math.floor(code/10) + 1, code%10 + 1;
    for i in range(len(pwd)):
        col, row = math.floor(i/space), i%space * (math.floor((len(pwd))/space) + 1);
        pwds[row + col] = chr(ord(pwd[i]) - increment);
        increment+=1;
    return "".join(pwds);