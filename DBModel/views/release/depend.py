import django.utils.timezone as timezone;
from DBModel import models;

from utils import base_util;

# 上传程序文件
def uploadExe(request, user, result, isSwitchTab):
    if not isSwitchTab:
        saveExe(request, user, result);
    # 所有线上工具的名称
    result["olNamelist"] = [exeInfo.name for exeInfo in models.Exe.objects.all().order_by('name')];
    # 返回线上版本数据
    result["onlineInfoList"] = getOlExeInfoList();

# 上传依赖库
def uploadDepend(request, user, result, isSwitchTab):
    if not isSwitchTab:
        saveDepend(request, user, result);
    # 所有线上依赖库的名称
    result["olNamelist"] = [exeInfo.name for exeInfo in models.Depend.objects.all().order_by('name')];
    # 返回线上版本信息
    result["onlineInfoList"] = getOlDependInfoList();

# 保存exe
def saveExe(request, name, result):
    name, path = request.POST.get("name", None), request.POST.get("path", None);
    version, file_path, changelog = request.POST.get("version", None), request.FILES.get("file", None), request.POST.get("changelog", None);
    if name and version and file_path and changelog:
        try:
            exe = models.Exe.objects.get(name = name);
        except Exception as e:
            exe = models.Exe(name = name, path = path);
            exe.save();
        # 保存程序详情
        vList = version.split(".");
        base_version = ".".join(vList[:1]);
        if  base_util.verifyVersion(version, [exeInfo.version for exeInfo in models.ExeDetail.objects.filter(base_version = base_version)]):
            exeDetail = models.ExeDetail(eid = exe, version = version, file_path = file_path, base_version = base_version, changelog = changelog, time = timezone.now());
            exeDetail.save();
            result["requestTips"] = f"更新文件【{name}, {version}】上传成功。";
        else:
            result["requestFailedTips"] = f"已存在更高的更新程序版本号，请修改版本号【{name}, {version}】后重试！";

# 获取线上信息列表
def getOlExeInfoList():
    exeList = models.ExeDetail.objects.all().order_by('time');
    exeList = exeList.values("base_version").distinct();
    if len(exeList) > 0:
        return [{
            "name" : exeInfo.eid.name,
            "version" : exeInfo.version,
            "time" : exeInfo.time,
            "changelog" : exeInfo.changelog,
            "url" : exeInfo.file_path.url,
        } for exeInfo in exeList];
    return [];

# 保存依赖库
def saveDepend(request, user, result):
    name, path = request.POST.get("name", None), request.POST.get("path", None);
    file_path, description = request.FILES.get("file", None), request.POST.get("description", None);
    if name and file_path and description:
        try:
            depend = models.Depend.objects.get(name = name);
            depend.file_path = file_path;
            depend.description = description;
            depend.save();
            result["requestTips"] =  f"依赖库【{name}】更新成功！";
        except Exception as e:
            depend = models.Depend(name = name, file_path = file_path, description = description, time = timezone.now());
            depend.save();
            result["requestTips"] = f"依赖库【{name}】上传成功。";

# 获取线上依赖库信息
def getOlDependInfoList():
    dependList = models.Depend.objects.all().order_by('time');
    if len(dependList) > 0:
        return [{
            "name" : dependInfo.name,
            "time" : dependInfo.time,
            "description" : dependInfo.description,
            "url" : dependInfo.file_path.url,
        } for dependInfo in dependList];
    return [];