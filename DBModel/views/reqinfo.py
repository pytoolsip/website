from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from DBModel import models
from base import *;

from _Global import _GG;

# 请求信息
@csrf_exempt
def reqinfo(request):
    _GG("Log").d("===== request info =====", request.GET);
    request.encoding = "utf-8";
    key, req = request.GET.get("key", ""), request.GET.get("req", "");
    if key == "ptip":
        if req == "verList":
            ptipList = models.Ptip.objects.filter(status = Status.Released.value);
            ptipList = ptipList.values("update_version").distinct().order_by('-update_version');
            return JsonResponse({"verList" : [ptip.version for ptip in ptipList]});
        elif req == "urlList":
            urlList = [];
            version = request.GET.get("version", "");
            ptipList = models.Ptip.objects.filter(status = Status.Released.value, version = version);
            if len(ptipList) > 0:
                # 平台信息
                ptipInfo = ptipList[0];
                urlList,append({"url" : ptipInfo.file_path.url, "path" : ""});
                # 依赖信息
                exeList, envList = json.loads(ptipInfo.exe_list), json.loads(ptipInfo.env_list);
                for exeInfo in exeList:
                    try:
                        exe = models.Exe.objects.get(name = exeInfo["name"]);
                        exeDetail = models.ExeDetail.objects.filter(eid = exe, base_version = exeInfo["base_version"]).order_by("-time")[0];
                        urlList.append({"url" : exeDetail.file_path.url, "path" : exe.path});
                    except Exception as e:
                        _GG("Log").d(e);
                for envInfo in envList:
                    try:
                        env = models.Depend.objects.get(name = envInfo["name"]);
                        urlList.append({"url" : env.file_path.url, "path" : env.path});
                    except Exception as e:
                        _GG("Log").d(e);
            return JsonResponse({"urlList" : urlList});
    return JsonResponse({});
