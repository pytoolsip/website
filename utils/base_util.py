
# 获取post数据的bool类型
def getPostAsBool(request, key):
    return request.POST.get(key, "") == "true";