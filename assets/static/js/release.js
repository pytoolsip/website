$(function(){
    // 请求管理后台
    requestManage = function(data){
        var userInfo = getUserLoginInfo();
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
        var userInfo = getUserLoginInfo();
        addInputToForm(item, "uname", userInfo.name, "text");
        addInputToForm(item, "upwd", userInfo.pwd, "text");
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
        // 重置玩家的登录信息
        setUserLoginInfo(null, null, 0);
        requestManage({});
    }
    // 点击登出
    $("#logoutButton").on("click",function(){
        logoutManage();
    });
})