$(function(){
    // 校验版本
    $.validator.addMethod(
        "checkVersion",
        function(value, element, param){
            if (!this.optional(element)) {
                return false;
            }
            var verList = value.split(".");
            if (verList.length != 3) {
                return false;
            }
            verList.forEach(function(item){
                if (!isNaN(Number(item))) {
                    return false;
                }
            });
            return true;
        },
        $.validator.format("请输入正确的版本格式（如，1.0.0）!")
    );
    // 校验文件类型
    $.validator.addMethod(
        "checkFileType",
        function(value, element, param){
            if (!this.optional(element)) {
                return false;
            }
            var valList = value.split(".");
            if (valList[valList.length-1] != param) {
                return false;
            }
            return true;
        },
        $.validator.format("请选择{0}格式的文件!")
    );
    // 校验工具
    $.validator.addMethod(
        "checkToolName",
        function(value, element, param){
            if (!this.optional(element)) {
                return false;
            }
            // 获取分类值
            var categorys = [];
            $("#category>select").each(function(index,element){
                categorys.push($(element).val())
            });
            $("#category>input").val().split("/").forEach(function(item){
                if (item != "") {
                    categorys.push(item);
                }
            });
            // 获取完整名称
            var tName = categorys.join("/") + value;
            // 校验工具(post方法)
            $.get(window.location.href, {"name" : tName}, function(data, status){
                if (status == "success") {
                    
                    $(element).addClass("");
                }
            });

            return true;
        },
        $.validator.format("请选择{0}格式的文件!")
    );
})