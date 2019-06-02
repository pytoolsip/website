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
    // 点击登出
    $("#logoutButton").on("click",function(){
        $.cookie("ptip_mg_username", null, {expires: 0.5, path: "/"});
        $.cookie("ptip_mg_userpwd", null, {expires: 0.5, path: "/"});
        requestManage({});
    });
})