$(function(){
    // 请求管理后台
    requestCallback = function(data, callback){
        $.post(window.location.href, data, function(data, status){
            if (status == "success") {
                $("#mainContent").html(data);
                updateFooterPosition(); // 更新footer的位置
            }
            callback();
        });
    }
    // 请求管理后台
    requestManage = function(data){
        requestCallback(data, function(){});
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
                updateFooterPosition(); // 更新footer的位置
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
        logoutIP(null, function(){
            requestManage({});
        });
    }
    // 点击登出
    $("#logoutButton").on("click",function(){
        logoutManage();
    });
})