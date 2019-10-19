from django.views.decorators.csrf import csrf_exempt
import django.utils.timezone as timezone
from django.http import JsonResponse,HttpResponse
from django.core.cache import cache
from django.core.mail import send_mail

from website import settings
from DBModel import models
from utils import base_util, pwd_util, random_util

from _Global import _GG;

import hashlib;
import random;

# 用户信息请求
@csrf_exempt
def userinfo(request):
    request.encoding = "utf-8";
    key = request.GET.get("k", "");
    if key == "login": # 登陆
        return login(request);
    elif key == "register": # 注册
        return register(request);
    elif key == "detail": # 用户详情
        return detail(request);
    return JsonResponse({"isSuccess" : False});

# 登陆页请求
def login(request):
    uname, upwd = request.POST.get("uname", ""), request.POST.get("upwd", "");
    _GG("Log").d("===== login =====", uname, upwd);
    return JsonResponse(getLoginInfo(uname, upwd = upwd, isLogin = base_util.getPostAsBool(request, "isLogin"), isRemember = base_util.getPostAsBool(request, "isRemember")));

# 获取登录信息
def getLoginInfo(uname, upwd = "", isLogin = False, isRemember = False):
    result = {"isSuccess" : False};
    # 获取登陆玩家
    userAuth = getLoginUserAuth(uname, upwd, isLogin);
    if userAuth:
        user = userAuth.uid;
        result = {
            "isSuccess" : True,
            "name" : user.name,
            "email" : user.email,
        };
        # 缓存玩家密码对应的md5
        if isLogin:
            randCode = random_util.randomNum(8); # 8位随机码
            result["pwd"] = hashlib.md5("|".join([userAuth.password, randCode]).encode("utf-8")).hexdigest();
            result["expires"] = 12*60*60; # 默认12小时
            if isRemember:
                result["expires"] = 10*24*60*60; # 10天
            # 缓存密码信息
            cache.set(result["pwd"], userAuth.password, result["expires"]);
            pwdKey = "|".join(["password", user.name, userAuth.password]);
            if cache.has_key(pwdKey) and cache.has_key(cache.get(pwdKey)):
                cache.delete(cache.get(pwdKey));
            cache.set(pwdKey, result["pwd"], result["expires"]);
    else:
        result["tips"] = "用户名和密码不匹配！";
    return result;

# 获取登陆玩家
def getLoginUserAuth(uname, upwd, isLogin = False):
    try:
        pwd = _GG("DecodeStr")(upwd);
        user = models.User.objects.get(name = uname);
        if isLogin:
            userAuth = models.UserAuthority.objects.get(uid = user);
            pwd = pwd_util.encodePassword(userAuth.salt, pwd);
        elif cache.has_key(pwd):
            # 从缓存中读取密码
            pwd = cache.get(pwd);
        # 返回数据
        _GG("Log").d("===== Get Login User By ===== :", uname, pwd);
        return models.UserAuthority.objects.get(uid = user, password = pwd);
    except Exception as e:
        _GG("Log").w(e);
    return None;

# 注册请求
def register(request):
    _GG("Log").d("register get :", request.GET, "; register post :", request.POST, "; register files :", request.FILES);
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
    return JsonResponse({});

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
    # 缓存验证码
    expires = 2*60; # 缓存2分钟
    cache.set("|".join(["verify_code", "register", email]), verifyCode, expires);
    # 发送邮件给指定邮箱
    try:
        send_mail("PyToolsIP", "平台验证码："+verifyCode, settings.EMAIL_HOST_USER, [email], fail_silently=False);
    except Exception as e:
        _GG("Log").w(e, f"-> verifyCode[{verifyCode}]");
        return JsonResponse({"isSuccess" : False, "tips" : "验证码发送失败，请检查邮箱是否正确！"});
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
    user = models.User(name = uname, email = email);
    user.save();
    models.UserAuthority(uid = user, password = password, salt = salt, authority = 0).save();
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
        # 获取用户权限数据
        if len(models.UserAuthority.objects.filter(uid = user)) == 0:
            models.UserAuthority(uid = user, password = "", salt = "", authority = 0).save();
        userAuth = models.UserAuthority.objects.get(uid = user);
    except Exception as e:
        _GG("Log").w(e);
        return JsonResponse({"isSuccess" : False, "tips" : "用户邮箱异常！"});
    # 更新密码及salt值
    pwd = _GG("DecodeStr")(upwd);
    userAuth.salt = random_util.randomMulti(32);
    userAuth.password = pwd_util.encodePassword(userAuth.salt, pwd);
    userAuth.save();
    return JsonResponse({"isSuccess" : True});

def detail(request):
    uname, upwd = request.POST.get("uname", ""), request.POST.get("upwd", "");
    # 获取登陆玩家
    userAuth = getLoginUserAuth(uname, upwd);
    if userAuth:
        user = userAuth.uid;
        return JsonResponse({
            "isSuccess" : True,
            "name" : user.name,
            "email" : user.email,
            "img" : user.img or "/pytoolsip/static/img/dzjh-icon.png",
            "bio" : user.bio or "",
        });
    return JsonResponse({"isSuccess" : False, "tips" : "用户状态异常！"});