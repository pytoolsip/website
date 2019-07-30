$(function(){
    // 获取玩家信息
    var getUserInfo = function(){
        var $uname = $.cookie("ptip_mg_username");
        var $upwd = $.cookie("ptip_mg_userpwd");
        if ($uname == undefined || $uname == "null") {
            $uname = "";
        }
        if ($upwd == undefined || $upwd == "null") {
            $upwd = "";
        }
        return {
            "name" : $uname,
            "pwd" : $upwd,
        };
    }
    // 请求管理后台
    requestManage = function(data){
        var userInfo = getUserInfo();
        data.uname = userInfo.name;
        data.upwd = userInfo.pwd;
        $.post(window.location.href, data, function(data, status){
            if (status == "success") {
                $("#mainContent").html(data);
            }
        });
    }
    // 添加input到form中
    var addInputToForm = function(item, name, value, type){
        var $input = item.find("input[name='" + name + "']");
        if ($input.length > 0) {
            $input.val(value);
            if ($input.attr("type") != type) {
                $input.attr("type", type)
            }
        } else {
            item.append("<input name='" + name + "' class='hidden' type='" + type + "' value='" + value + "' />");
        }
    }
    // 添加数据到表单
    var addInputsToForm = function(item, exIpts){
        // 添加扩展输入
        if (exIpts instanceof Array && exIpts.length > 0) {
            for (var i = 0; i < exIpts.length; i++) {
                var ipt = exIpts[i];
                addInputToForm(item, ipt.key, ipt.val, ipt.type);
            }
        }
        // 添加用户名和密码
        var $uname = $.cookie("ptip_mg_username");
        var $upwd = $.cookie("ptip_mg_userpwd");
        if ($uname == undefined || $uname == "null") {
            $uname = "";
        }
        if ($upwd == undefined || $upwd == "null") {
            $upwd = "";
        }
        addInputToForm(item, "uname", $uname, "text");
        addInputToForm(item, "upwd", $upwd, "text");
    }
    // 添加用户信息到表单
    uploadManageForm = function(item, exIpts){
        if (item.length == 0) {
            return;
        }
        // 添加数据到表单
        addInputsToForm(item, exIpts);
        // 提交数据
        $.ajax({
            url : window.location.href,
            type : "post",
            data : new FormData(item[0]),
            processData : false,
            contentType : false,
            success : function(data){
                $("#mainContent").html(data);
            },
            error: function(e) {
                console.log(e);
                alert("提交表单失败！");
            }
        })
    }
    // 登出管理后台
    logoutManage = function(){
        $.cookie("ptip_mg_username", null, {expires: 0.5, path: "/"});
        $.cookie("ptip_mg_userpwd", null, {expires: 0.5, path: "/"});
        requestManage({});
    }
    // 点击登出
    $("#logoutButton").on("click",function(){
        logoutManage();
    });
    // 登陆管理后台
    loginManage = function(name, pwd, encodePwd){
        $.post(window.location.href, {
            isReqLogin : true,
            uname : name,
        }, function(data, status){
            if (status == "success") {
                if (!data.isSuccess) {
                    alert("用户名和密码不匹配！");
                    return;
                }
                $.post(window.location.href, {
                    isLogin : true,
                    uname : name,
                    upwd : encodePwd(pwd, parseInt(data.code)),
                }, function(data, status){
                    if (status == "success") {
                        if (!data.isSuccess) {
                            alert("用户名和密码不匹配！");
                            return;
                        }
                        $.cookie("ptip_mg_username", data.name, {expires: 0.5, path: "/"});
                        $.cookie("ptip_mg_userpwd", data.pwd, {expires: 0.5, path: "/"});
                        requestManage({});
                    } else {
                        alert("登陆失败！")
                    }
                });
            } else {
                alert("请求登陆失败！")
            }
        });
    }
})