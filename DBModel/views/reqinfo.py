from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from DBModel import models

from _Global import _GG;

# 请求信息
@csrf_exempt
def reqinfo(request):
    _GG("Log").d("===== request info =====", request.GET);
    key, req = request.GET.get("key", ""), request.GET.get("req", "");
    if key == "ptip":
        if req == "verList":
            ptipList = models.Ptip.objects.filter(status = Status.Released.value);
            ptipList = ptipList.values("update_version").distinct().order_by('update_version');
            return JsonResponse({"verList" : [ptip.version for ptip in ptipList]});
        elif req == "urlList":
            urlList = [];
            version = request.GET.get("version", "");
            ptipList = models.Ptip.objects.filter(status = Status.Released.value, version = version);
            if len(ptipList) > 0:
                ptipInfo = ptipList[0];
                exeList, envList = json.loads(ptipInfo.exe_list), json.loads(ptipInfo.env_list);
                urlList,append({"url" : ptipInfo.file_path.url, "path" : ""});
                urlList.extend(exeList);
                urlList.extend(envList);
            return JsonResponse({"urlList" : urlList});
    return JsonResponse({});
