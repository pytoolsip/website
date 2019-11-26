from django.core.cache import cache;
import qrcode;
import io;
import base64;
import uuid;
import hashlib;
import time;

from _Global import _GG;
from DBModel.consumers.base import BaseConsumer;

# Login WebSocket Consumer
class LoginConsumer(BaseConsumer):
    """docstring for LoginConsumer"""
    def __init__(self, *args, **kw):
        super(LoginConsumer, self).__init__(*args, baseName = "pytoolsip_web_", **kw);
        self.__loginID = "";
        self.initListener();
        pass;
    
    def initListener(self):
        for name in ["ReqLoginID", "ReqQrcode"]:
            self.register(name, getattr(self, name));
        pass;

    def __delLoginID__(self):
        _GG("ConsumerMgr").removeLoginConsumer(self.__loginID, self);
        pass;

    def __updateLoginID__(self, lid):
        self.__delLoginID__();
        self.__loginID = lid;
        _GG("ConsumerMgr").addLoginConsumer(self.__loginID, self);
        pass;

    def onClose(self, closeCode):
        self.__delLoginID__();
        pass;
    
    def ReqLoginID(self, ctx, msg):
        # 获取新loginID
        lid = ctx.get(self.getBaseName("login_id"), "");
        if not lid:
            lid = str(uuid.uuid1());
            while len(_GG("ConsumerMgr").getLoginConsumers(lid)) > 0:
                lid = str(uuid.uuid1());
        # 更新loginID
        self.__updateLoginID__(lid);
        # 更新ctx
        self.updateCtx({self.getBaseName("login_id") : lid});
        pass;
    
    def ReqQrcode(self, ctx, msg):
        loginMd5 = hashlib.md5("|".join([self.__loginID, str(time.time())]).encode("utf-8")).hexdigest();
        expires = 2*60; # 默认2分钟
        cache.set(loginMd5, self.__loginID, expires); # 缓存登陆md5信息
        # 生成二维码
        qr = qrcode.QRCode(version=10);
        qr.add_data(loginMd5);
        qr.make(fit=True);
        img = qr.make_image();
        # 生成base64码
        imgBuffer = io.BytesIO();
        img.save(imgBuffer, "png");
        imgB64 = base64.b64encode(imgBuffer.getvalue());
        imgBuffer.close();
        # 返回数据
        return {
            "qrcode" : imgB64.decode(),
            "expires" : expires,
        };

    def onLogin(self, token, expires):
        self.notify("OnLogin", {"pytoolsip_token" : _GG("EncodeStr")(token), "expires" : expires});
