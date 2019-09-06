import hashlib;

# 获取post数据的bool类型
def getPostAsBool(request, key):
    return request.POST.get(key, "") == "true";

# 校验分类
def _verifyCategory_(category, isAddSlash = True):
    category = category.replace(" ", "");
    if len(category) > 0:
        if isAddSlash and category[-1] != "/":
            category += "/";
        elif category[-1] == "/":
            category = category[:-1];
    return category;

# 获取md5码
def _getMd5_(name, category):
    name = _verifyCategory_(category) + name;
    return hashlib.md5(name.encode("utf-8")).hexdigest();

# 分离版本号
def _splitVersion_(version):
    return [int(ver) for ver in version.replace(" ", "").split(".") if ver.isdigit()];

# 校验提交的版本
def verifyVersion(ver, olVerList):
    verList = _splitVersion_(ver);
    for olVer in olVerList:
        if ver == olVer:
            return False;
        for i, v in enumerate(_splitVersion_(olVer)):
            if v > verList[i]:
                return False;
    return True;
