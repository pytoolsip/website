import math;
import random;

import re,os,sys,time;

# 当前文件位置
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__));
# 添加搜索路径
if CURRENT_PATH not in sys.path:
	sys.path.append(CURRENT_PATH);
if os.path.join(CURRENT_PATH, "core") not in sys.path:
	sys.path.append(os.path.join(CURRENT_PATH, "../", "core"));

from rsaCore import encodeStr, decodeStr, getPublicKey;

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

def testRand(rlStartIdx = None, total = 20):
    limit = 9;
    interval = int(total / limit);
    if interval > 0:
        tmpTotal = total + (limit - total % limit) % limit;
        def getNextIdx(curIdx):
            nextIdx = (curIdx + interval) % tmpTotal;
            if nextIdx == nextIdx % interval and interval > 1:
                nextIdx += 1;
            while nextIdx >= total:
                nextIdx = (nextIdx + interval) % tmpTotal;
            return nextIdx;
        # 获取开始下标
        startIdx = 0;
        if rlStartIdx and 0 <= rlStartIdx <= total:
            startIdx = rlStartIdx;
        # 获取返回列表
        print("getRecommendList:", tmpTotal, interval, startIdx);
        idxList = [];
        while len(idxList) < limit:
            print("getRecommendList startIdx:", startIdx, idxList);
            if startIdx in idxList:
                break;
            # 添加返回信息
            idxList.append(startIdx);
            # 获取下一个下标
            startIdx = getNextIdx(startIdx);
            print("getRecommendList while:", startIdx, idxList);
        return idxList;
    

if __name__ == '__main__':
    # code = "91"; # getEncodeCode();
    # print("==== code ====", code);
    # pwd = decodePwd("-r9{|jkqr}~=>@ACDFGIJ", int(code));
    # print("==== pwd ====", pwd);
    # t = encodeStr("just test 199999");
    # print("t:", t)
    # print("result:", decodeStr(t));
    # name = "梦心DH"
    # nb = name.encode();
    # # bytes.decode()
    # print(nb, bytes.decode(nb))
    print(testRand(14));