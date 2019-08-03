import math;
import random;

# 获取编码值
def getEncodeCode():
    return "".join([str(random.randint(1,9)), str(random.randint(1,2))]); # 编码值

# 获取编码密码函数
def getEncodePwdFunc(code):
    return """(function(pwd, code){
            var pwds = [];
            var lastCode = "";
            var space = Math.floor(code/10) + 1;
            var increment = code%10 + 1;
            pwds.push(String.fromCharCode(pwd.length + increment + 32));
            for (var i = 0; i < space; i++) {
                for (var j = 0; j < Math.ceil((pwd.length)/space); j++){
                    var idx = i+j*space;
                    if (idx < pwd.length){
                        lastCode = pwd.charCodeAt(idx);
                    }
                    pwds.push(String.fromCharCode(lastCode + increment));
                    increment++;
                }
            }
            return pwds.join("");
        })('$1', """+code+")";

# 解码登陆密码
def decodePwd(pwd, code):
    space, increment = math.floor(code/10) + 1, code%10 + 1;
    pwdsLen = ord(pwd[0]) - increment - 32;
    pwds, pwdIdx = [""] * pwdsLen, 1;
    for i in range(space):
        for j in range(math.ceil(pwdsLen/space)):
            idx = i+j*space;
            if idx < pwdsLen and pwdIdx < len(pwd):
                pwds[idx] = chr(ord(pwd[pwdIdx]) - increment);
            pwdIdx+=1;
            increment+=1;
    return "".join(pwds);