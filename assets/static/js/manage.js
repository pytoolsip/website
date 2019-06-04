$(function(){
    // 请求管理后台
    requestManage = function(data){
        var $uname = $.cookie("ptip_mg_username");
        var $upwd = $.cookie("ptip_mg_userpwd");
        if ($uname == undefined || $uname == "null") {
            $uname = "";
        }
        if ($upwd == undefined || $upwd == "null") {
            $upwd = "";
        }
        data.uname = $uname;
        data.upwd = $upwd;
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
    var addInputsToForm = function(item, mk){
        // 添加mk
        addInputToForm(item, "mk", mk, "text");
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
    uploadManageForm = function(item, mk){
        if (item.length == 0) {
            return;
        }
        // 添加数据到表单
        addInputsToForm(item, mk);
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
    // 点击登出
    $("#logoutButton").on("click",function(){
        $.cookie("ptip_mg_username", null, {expires: 0.5, path: "/"});
        $.cookie("ptip_mg_userpwd", null, {expires: 0.5, path: "/"});
        requestManage({});
    });
})