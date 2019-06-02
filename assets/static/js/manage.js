$(function(){
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
    $("#sidebar ._slideItem_").on("click", function(){
        var $selected = $("#sidebar li.active").toggleClass("active");
        if ($selected != $(this).parent()) {
            $(this).parent().toggleClass("active");
            // 请求信息
            requestManage({
                k : $(this).attr("data-target"),
            });
        }
    });
})