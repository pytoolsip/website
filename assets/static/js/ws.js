$(function(){
    var loginUrl = "";
    // 登陆Socket的构造函数
    var LoginSocket = function(qrcodeCallback) {
        this.ws = new WebSocket("ws://" + loginUrl);
        this.qrcodeCallback = qrcodeCallback;
        this.init();
    };
    // 初始化登陆Socket
    LoginSocket.prototype.init = function() {
        var self = this;
        self.ws.onopen = function(e) {
            self.ws.send(JSON.stringify({
                "key" : "id",
                "msg": $.cookie("login_id"),
            }));
        }
        self.ws.onclose = function(e) {
            self.qrcodeCallback("invalid", msg);
            console.log("socket closed !");
        }
        self.ws.onmessage = function(e) {
            var data = JSON.parse(e.data);
            if (data.hasOwnProperty("key") && data.hasOwnProperty("msg")) {
                var msg = data["msg"];
                switch (data["key"]) {
                    case "id":
                        $.cookie("login_id", msg);
                        break;
                    case "qrcode":
                        self.qrcodeCallback("valid", msg);
                        break;
                    case "invalid_qrcode":
                        self.qrcodeCallback("invalid", msg);
                        break;
                }
            }
        }
    };
    LoginSocket.prototype.isOpen = function() {
        return this.ws.readyState == this.ws.OPEN;
    };
    LoginSocket.prototype.request = function() {
        if (this.isOpen()) {
            this.ws.send(JSON.stringify({
                "key" : "qrcode",
            }));
        }
    };
    LoginSocket.prototype.close = function() {
        if (this.isOpen()) {
            this.ws.close();
        }
    };
    // 新建登陆Socket的全局函数
    newLoginSocket = function(callback) {
        if (window.WebSocket) {
            return new LoginSocket(callback);
        } else {
            return null;
        }
    };
})