from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse

from DBModel import models

import hashlib;
import random;

# 登陆页请求
@csrf_exempt
def login(request):
    uname, upwd = request.POST.get("uname", ""), request.POST.get("upwd", "");
    if request.POST.get("isReqLogin", False):
        return JsonResponse(getLoginInfo(uname, isReq = True));
    if request.POST.get("isLogin", False):
        JsonResponse(getLoginInfo(uname, upwd = upwd, isLogin = True));
    return JsonResponse(getLoginInfo(uname, upwd = upwd));

# 获取登录信息
def getLoginInfo(uname, upwd = "", isReq = False, isLogin = False):
    result = {"isSuccess" : False};
    code = "21"; # "".join([str(i) for i in random.sample(range(10), 2)]); # 编码值
    if isReq:
        if len(models.User.objects.filter(name = uname)) == 0:
            return JsonResponse({
                "isSuccess" : False,
                "tips" : "用户名不存在！",
            });
        return JsonResponse({
            "isSuccess" : True,
            "encodePwd" : getEncodePwd(code),
        });
    try:
        pwd = upwd;
        if isLogin:
            pwd = decodePwd(upwd, int(code));
        else:
            # 从缓存中读取pwd
            pass;
        print("===== Get Login User By ===== :", uname, pwd);
        user = models.User.objects.get(name = uname, password = pwd);
        return {
            "isSuccess" : True,
            "name" : user.name,
            "email" : user.email,
            "pwd": hashlib.md5(user.password.encode("utf-8")).hexdigest(),
        };
    except Exception as e:
        result["tips"] = "用户名和密码不匹配！";
    return result;

# 获取编码密码函数
def getEncodePwd(code):
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
        })($1, """+code+")";

# 解码登陆密码
def decodePwd(pwd, code):
    pwds = [""] * len(pwd);
    space, increment = math.floor(code/10) + 1, code%10 + 1;
    for i in range(len(pwd)):
        col, row = math.floor(i/space), i%space * (math.floor((len(pwd))/space) + 1);
        pwds[row + col] = chr(ord(pwd[i]) - increment);
        increment+=1;
    return "".join(pwds);