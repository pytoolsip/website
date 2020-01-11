from django.core.cache import cache;

from DBModel import models;
from utils import pwd_util;

from DBModel.views.userinfo import getLoginUserAuth, getLoginToken;

from app import home;

from _Global import _GG;
from base import *;

# App WebSocket Consumer
class AppConsumer(BaseConsumer):
    """docstring for AppConsumer"""
    def __init__(self, *args, **kw):
        super(AppConsumer, self).__init__(*args, baseName = "pytoolsip_app_", **kw);
        self.initListener();
        pass;
    
    def initListener(self):
        for name in ["LoginWeb", "Login"]:
            self.register(name, getattr(self, name));
        pass;

    def onConnect(self):
        _GG("ConsumerMgr").addAppConsumer(id(self), self);
        pass;

    def onClose(self, closeCode):
        _GG("ConsumerMgr").removeAppConsumer(id(self));
        pass;

    def onCheckCtx(self, ctx):
        ctx["userAuth"] = None;
        ctx["user"] = None;
        # 根据token信息获取用户信息
        token = _GG("DecodeStr")(ctx.get("pytoolsip_app_token", ""));
        uinfo = token.split("|token|");
        if len(uinfo) == 2:
            uname, upwd = uinfo;
            ctx["userAuth"] = getLoginUserAuth(uname, upwd); # 包含用户权限的用户信息
            if ctx["userAuth"]:
                ctx["user"] = ctx["userAuth"].uid;
        return True;

    def LoginWeb(self, ctx, msg):
        result = {"isSuccess" : False};
        userAuth = ctx["userAuth"];
        if not userAuth:
            result["tips"] = "用户数据异常！";
            return;
        loginMd5 = msg.get("login_md5", "");
        if not cache.has_key(loginMd5):
            result["tips"] = "登陆二维码已过期！";
            return;
        loginID = cache.get(loginMd5);
        consumers = _GG("ConsumerMgr").getLoginConsumers(loginID);
        if len(consumers) == 0:
            result["tips"] = "登陆页面已关闭！";
            return;
        # 生成网页token
        token, expires = getLoginToken(result, userAuth.uid.name, userAuth.password);
        if result["isSuccess"]: # 如果登录成功，则发送给对应ID的所有登录socket
            for ws in consumers:
                ws.onLogin(token, expires);
        return result;
    
    def Login(self, ctx, msg):
        result = {"isSuccess" : False, "pytoolsip_app_token" : ""};
        # 获取登陆玩家
        uname, upwd = msg.get("uname", ""), msg.get("upwd", "");
        userAuth = getLoginUserAuth(uname, _GG("DecodeStr")(upwd), True);
        if userAuth:
            user = userAuth.uid;
            result["isSuccess"] = True;
            # 缓存玩家密码对应的md5
            pwdMd5 = hashlib.md5("|app_pwd|".join([userAuth.password, str(time.time())]).encode("utf-8")).hexdigest();
            # 缓存密码信息
            expires = 30*24*60*60; # 默认30天
            cache.set(pwdMd5, userAuth.password, expires);
            pwdKey = "|".join(["app_pwd", user.name, userAuth.password]);
            if cache.has_key(pwdKey) and cache.has_key(cache.get(pwdKey)):
                cache.delete(cache.get(pwdKey));
            cache.set(pwdKey, pwdMd5, expires);
            # 生成token
            result["pytoolsip_app_token"] = "|app_token|".join([user.name, pwdMd5]);
        else:
            result["tips"] = "用户名和密码不匹配！";
        return result;
    
    def Follow(self, ctx, msg):
        if not ctx["userAuth"]:
            return {"isSuccess" : False};
        return {"isSuccess" : True};
    
    def ReqAllArticles(self, ctx, msg):
        return home.reqAllArticles(ctx, msg);
    
    def ReqAllUsers(self, ctx, msg):
        return home.reqAllUsers(ctx, msg);
    
    def notice(self, data):
        self.notify("OnNotice", data);