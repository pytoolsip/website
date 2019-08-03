import math;

# 获取编码密码函数
def getEncodePwdFunc(code):
    return """(function(pwd, code){
            var pwds = [];
            var space = Math.floor(code/10) + 1;
            var increment = code%10 + 1;
            for (var i = 0; i < pwd.length; i ++) {
                var col = Math.floor(i/space);
                var row = i%space * (Math.floor((pwd.length)/space) + 1);
                pwds.push(String.fromCharCode(pwd.charCodeAt(row + col) + increment));
                increment++;
            }
            return pwds.join("");
        })('$1', """+code+")";

# 解码登陆密码
def decodePwd(pwd, code):
    pwds = [""] * len(pwd);
    space, increment = math.floor(code/10) + 1, code%10 + 1;
    for i in range(len(pwd)):
        col, row = math.floor(i/space), i%space * (math.floor((len(pwd))/space) + 1);
        pwds[row + col] = chr(ord(pwd[i]) - increment);
        increment+=1;
    return "".join(pwds);