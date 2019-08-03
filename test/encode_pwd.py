import math;
import random;

# 获取编码值
def getEncodeCode():
    return "".join([str(random.randint(1,9)), str(random.randint(1,2))]); # 编码值

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

if __name__ == '__main__':
    code = "91"; # getEncodeCode();
    print("==== code ====", code);
    pwd = decodePwd("-r9{|jkqr}~=>@ACDFGIJ", int(code));
    print("==== pwd ====", pwd);