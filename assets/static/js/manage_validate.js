$(function(){
    // 校验版本
    $.validator.addMethod(
        "checkVersion",
        function(value, element, param){
            if (this.optional(element)) {
                return false;
            }
            var verList = value.split(".");
            console.log("checkVersion::verList:", verList);
            if (verList.length != param) {
                return false;
            }
            var ret = true;
            verList.forEach(function(item){
                ret = /^\d+$/.test(item)
            });
            return ret;
        },
        "请输入正确的版本格式（如，1.0.0）"
    );
    // 校验文件类型
    $.validator.addMethod(
        "checkFileType",
        function(value, element, param){
            if (this.optional(element)) {
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
})