import django.utils.timezone as timezone;
from DBModel import models;

import hashlib;

from utils import base_util;

from _Global import _GG;

from base import *

# 上传程序文件
def uploadExe(request, userAuth, result, isSwitchTab):
    if not isSwitchTab:
        saveExe(request, userAuth, result);
    # 所有线上工具的名称
    result["olExeInfolist"] = [{"name" : exeInfo.name, "path" : exeInfo.path} for exeInfo in models.Exe.objects.all().order_by('-name')];
    # 返回线上版本数据
    result["onlineInfoList"] = getOlExeInfoList();

# 上传依赖库
def uploadDepend(request, userAuth, result, isSwitchTab):
    if not isSwitchTab:
        saveDepend(request, userAuth, result);
    # 所有线上依赖库的名称
    result["olDependInfolist"] = [{"name" : dependInfo.name, "path" : dependInfo.path} for dependInfo in models.Depend.objects.all().order_by('-name')];
    # 返回线上版本信息
    result["onlineInfoList"] = getOlDependInfoList();

# 保存exe
def saveExe(request, userAuth, result):
    name, path = request.POST.get("name", None), request.POST.get("path", None);
    version, file_path, changelog = request.POST.get("version", None), request.FILES.get("file", None), request.POST.get("changelog", None);
    if name and path and version and file_path and changelog:
        try:
            exe = models.Exe.objects.get(name = name);
            exe.path = path;
            exe.save();
        except Exception as e:
            _GG("Log").w(e);
            exe = models.Exe(name = name, path = path);
            exe.save();
        # 保存程序详情
        vList = version.split(".");
        base_version = ".".join(vList[:2]);
        if base_util.verifyVersion(version, [exeInfo.version for exeInfo in models.ExeDetail.objects.filter(base_version = base_version)]):
            exeDetail = models.ExeDetail(eid = exe, version = version, file_path = file_path, base_version = base_version, changelog = changelog, time = timezone.now());
            exeDetail.save();
            # 删除除指定版本外的其他版本
            delOtherVers(version);
            result["requestTips"] = f"更新文件【{name}, {version}】上传成功。";
        else:
            result["requestFailedTips"] = f"已存在更高的依赖程序版本号，请修改版本号【{name}, {version}】后重试！";
    else:
        result["requestFailedTips"] = f"上传依赖程序的信息不完整，请重新上传！";

# 获取线上信息列表
def getOlExeInfoList():
    exeList = models.ExeDetail.objects.all().order_by('-time');
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
def saveDepend(request, userAuth, result):
    name, path = request.POST.get("name", None), request.POST.get("path", None);
    file_path, description = request.FILES.get("file", None), request.POST.get("description", None);
    if name and path and file_path and description:
        file_key = hashlib.md5(file_path.read()).hexdigest();
        try:
            depend = models.Depend.objects.get(name = name);
            depend.path = path;
            depend.file_path = file_path;
            depend.file_key = file_key;
            depend.description = description;
            depend.time = timezone.now();
            depend.save();
            result["requestTips"] =  f"依赖库【{name}】更新成功！";
        except Exception as e:
            _GG("Log").w(e);
            depend = models.Depend(name = name, path = path, file_path = file_path, file_key = file_key, description = description, time = timezone.now());
            depend.save();
            result["requestTips"] = f"依赖库【{name}】上传成功。";
    else:
        result["requestFailedTips"] = f"上传依赖库的信息不完整，请重新上传！";

# 获取线上依赖库信息
def getOlDependInfoList():
    dependList = models.Depend.objects.all().order_by('-time');
    if len(dependList) > 0:
        return [{
            "name" : dependInfo.name,
            "time" : dependInfo.time,
            "description" : dependInfo.description,
            "url" : dependInfo.file_path.url,
        } for dependInfo in dependList];
    return [];

# 删除除指定版本外的其他版本
def delOtherVers(version):
    base_version = ".".join(version.split(".")[:2]);
    if len(models.ExeDetail.objects.filter(base_version = base_version, version = version)) > 0:
        for ptip in models.ExeDetail.objects.filter(base_version = base_version):
            if ptip.version != version:
                ptip.delete();
    else:
        _GG("Log").w(f"不存在指定版本【{version}】的依赖程序，故不能删除除此版本外的其他版本！");