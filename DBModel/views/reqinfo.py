from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from DBModel import models
from base import *;

import json;

from _Global import _GG;

ptipPath = "";

# 请求信息
@csrf_exempt
def reqinfo(request):
    _GG("Log").d("===== request info =====", request.GET);
    key, req = request.GET.get("key", ""), request.GET.get("req", "");
    if key == "ptip":
        if req == "verList":
            return JsonResponse({"verList" : getVerListByUpdateVer()});
        elif req == "urlList":
            urlList = [];
            version = request.GET.get("version", "");
            ptipList = models.Ptip.objects.filter(status = Status.Released.value, version = version);
            if len(ptipList) > 0:
                # 平台信息
                ptipInfo = ptipList[0];
                urlList.append({"url" : ptipInfo.file_path.url, "path" : ptipPath});
                # 依赖信息
                exeList, envList = json.loads(ptipInfo.exe_list), json.loads(ptipInfo.env_list);
                for exeInfo in exeList:
                    try:
                        exe = models.Exe.objects.get(name = exeInfo["name"]);
                        exeDetail = models.ExeDetail.objects.filter(eid = exe, base_version = exeInfo["base_version"]).order_by("-time")[0];
                        urlList.append({"name" : exeInfo["name"], "url" : exeDetail.file_path.url, "path" : exe.path});
                    except Exception as e:
                        _GG("Log").d(e);
                for envInfo in envList:
                    try:
                        env = models.Depend.objects.get(name = envInfo["name"]);
                        urlList.append({"name" : envInfo["name"], "url" : env.file_path.url, "path" : env.path});
                    except Exception as e:
                        _GG("Log").d(e);
            return JsonResponse({"urlList" : urlList});
    return JsonResponse({});

# 根据更新版本，获取版本列表
def getVerListByUpdateVer():
    verList, updateVerList = [], [];
    ptipList = models.Ptip.objects.filter(status = Status.Released.value).order_by("-update_version", "-time");
    for ptip in ptipList:
        if ptip.update_version not in updateVerList:
            verList.append(ptip.version);
        updateVerList.append(ptip.update_version);
    return verList;
