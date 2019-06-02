$(function(){
    // 请求管理后台
    requestManage = function(data){
        var $uname = $.cookie("ptip_mg_username");
        var $upwd = $.cookie("ptip_mg_userpwd");
        if ($uname == undefined || $uname == "null" || $upwd == undefined || $upwd == "null") {
            window.location.href = window.location.href;
            return;
        }
        data.uname = $uname;
        data.upwd = $upwd;
        $.post(window.location.href, data, function(data, status){
            if (status == "success") {
                var newDoc = document.open("text/html", "replace");
                newDoc.write(data);
                newDoc.close();
            }
        });
    }
    // 点击登陆
    $("#loginButton").on("click",function(){
        $.post(window.location.href, {
            isLogin : true,
            uname : $("#loginUserName").val(),
            upwd : $("#loginPassword").val(),
        }, function(data, status){
            if (status == "success" && data.isSuccess) {
                $.cookie("ptip_mg_username", data.name, {expires: 0.5, path: "/"});
                $.cookie("ptip_mg_userpwd", data.pwd, {expires: 0.5, path: "/"});
                requestManage({});
            } else {
                alert("登陆失败！")
            }
        });
    });
    // 切换tab
    $("#sidebar ._slideItem_").on("click", function(){
        var $selected = $("#sidebar li.active").toggleClass("active");
        if ($selected != $(this).parent()) {
            $(this).parent().toggleClass("active");
            // 请求信息
            requestManage({
                mk : $(this).attr("data-target"),
            });
        }
    });
})