from channels.generic.websocket import WebsocketConsumer;
import json;

from _Global import _GG;

# Base WebSocket Consumer
class BaseConsumer(WebsocketConsumer):
    """docstring for BaseConsumer"""
    def __init__(self, *args, baseName = "", **kw):
        super(BaseConsumer, self).__init__(*args, **kw);
        self.__baseName = baseName;
        self.__listeners = {};
        pass;

    def connect(self):
        self.accept();
        if hasattr(self, "onConnect"):
            getattr(self, "onConnect")();
        pass;

    def disconnect(self, close_code):
        if hasattr(self, "onClose"):
            getattr(self, "onClose")(close_code);
        pass;

    def getBaseName(self, suffix = ""):
        return self.__baseName + suffix;

    def updateCtx(self, ctx):
        self.notify("WS_onUpdateCtx", ctx);
        pass;

    def receive(self, text_data):
        _GG("Log").d("ws receive:", text_data);
        data = json.loads(text_data);
        # 校验数据
        if "req" not in data:
            self.notify("WS_onError", "Error! No Req!");
            return;
        if "ctx" not in data:
            self.notify("WS_onError", "Error! No Ctx!");
            return;
        if "msg" not in data:
            self.notify("WS_onError", "Error! No Msg!");
            return;
        # 处理数据
        reqName = data["req"];
        resp, status = {}, "success";
        if reqName in self.__listeners:
            ctx = data["ctx"];
            # 校验上下文内容
            if hasattr(self, "onCheckCtx"):
                if getattr(self, "onCheckCtx")(ctx):
                    resp = self.__listeners[reqName](ctx, data["msg"]);
                else:
                    status = "failure";
            else:
                resp = self.__listeners[reqName](ctx, data["msg"]);
        else:
            status = "failure";
        # 发送消息
        if "resp" in data and data["resp"]:
            self.notify(data["resp"], resp, status = status);
        pass;

    def notify(self, resp, msg, status = "success"):
        # _GG("Log").d("ws notify:", resp, msg, status);
        self.send(text_data=json.dumps({
            "resp" : resp,
            "msg" : msg,
            "status" : status,
        }));
        pass;

    def register(self, name, func):
        self.__listeners[name] = func;
        pass;

    def unregister(self, name):
        if name in self.__listeners:
            self.__listeners.pop(name);
        pass;