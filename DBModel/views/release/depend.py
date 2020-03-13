import django.utils.timezone as timezone;
from DBModel import models;

import hashlib;

from utils import base_util;

from _Global import _GG;

from release.base import *

# 上传程序文件
def uploadExe(request, userAuth, result, isSwitchTab):
    if not isSwitchTab:
        if request.POST.get("opType", "") == "delete":
            edid = request.POST.get("id", "");
            try:
                exeDetail = models.ExeDetail.objects.get(id = int(edid));
                exeDetail.delete();
                if len(models.ExeDetail.objects.filter(eid = exeDetail.eid)) == 0:
                    exeDetail.eid.delete();
                result["requestTips"] =  f"依赖程序【{exeDetail.eid.name}，{exeDetail.version}】成功下架！";
                # 发送邮件通知
                sendMsgToAllMgrs(f"管理员【{userAuth.uid.name}】于{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}，下架了【{exeDetail.eid.name}，{exeDetail.version}】依赖程序。");
            except Exception as e:
                _GG("Log").w(e);
                result["requestFailedTips"] = f"依赖程序【{edid}】下架失败。";
        else:
            saveExe(request, userAuth, result);
    # 所有线上工具的名称
    result["olExeInfolist"] = [{"name" : exeInfo.name, "path" : exeInfo.path} for exeInfo in models.Exe.objects.all().order_by('-name')];
    # 返回线上版本数据
    result["onlineInfoList"] = [{
        "id" : exeInfo.id,
        "name" : exeInfo.eid.name,
        "version" : exeInfo.version,
        "time" : exeInfo.time,
        "changelog" : exeInfo.changelog,
        "url" : exeInfo.file_path.url,
    } for exeInfo in models.ExeDetail.objects.all().order_by('-time')];

# 上传依赖库
def uploadDepend(request, userAuth, result, isSwitchTab):
    if not isSwitchTab:
        if "examType" in request.POST:
            examDepend(request, userAuth, result);
        else:
            name, path = request.POST.get("name", None), request.POST.get("path", None);
            file_path, description = request.FILES.get("file", None), request.POST.get("description", None);
            if name and path and file_path and description:
                file_key = hashlib.md5(file_path.read()).hexdigest();
                depend = models.Depend(name = name, path = path, file_path = file_path, file_key = file_key, description = description, time = timezone.now(), status = Status.Examing.value);
                depend.save();
                result["requestTips"] = f"依赖库【{name}】上传成功，正在等待审核。";
            else:
                result["requestFailedTips"] = f"上传依赖程序的信息不完整，请重新上传！";
    # 所有线上依赖库的名称
    result["olDependInfolist"] = [{"name" : dependInfo.name, "path" : dependInfo.path} for dependInfo in models.Depend.objects.filter(status = Status.Released.value).order_by('-name')];
    # 返回线上依赖库信息
    result["onlineInfoList"] = [{
        "id" : dependInfo.id,
        "name" : dependInfo.name,
        "time" : dependInfo.time,
        "description" : dependInfo.description,
        "url" : dependInfo.file_path.url,
    } for dependInfo in models.Depend.objects.filter(status = Status.Released.value).order_by('-time')];
    # 返回审核中信息
    dependList = models.Depend.objects.filter(status = Status.Examing.value).order_by('-time');
    if len(dependList) > 0:
        result["examInfoList"] = [{
            "id" : dependInfo.id,
            "name" : dependInfo.name,
            "time" : dependInfo.time,
            "description" : dependInfo.description,
            "url" : dependInfo.file_path.url,
        } for dependInfo in dependList];


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
        if base_util.verifyVersion(version, [exeInfo.version for exeInfo in models.ExeDetail.objects.filter(eid = exe, base_version = base_version)]):
            exeDetail = models.ExeDetail(eid = exe, version = version, file_path = file_path, base_version = base_version, changelog = changelog, time = timezone.now());
            exeDetail.save();
            # 删除除指定版本外的其他版本
            delOtherVers(exe, version);
            result["requestTips"] = f"更新文件【{name}, {version}】上传成功。";
        else:
            result["requestFailedTips"] = f"已存在更高的依赖程序版本号，请修改版本号【{name}, {version}】后重试！";
    else:
        result["requestFailedTips"] = f"上传依赖程序的信息不完整，请重新上传！";

# 审核依赖库
def examDepend(request, userAuth, result):
    examType, did, reason = request.POST.get("examType", None), request.POST.get("id", ""), request.POST.get("reason", "");
    if examType and did:
        try:
            depend = models.Depend.objects.get(id = int(did));
            if examType == "release":
                # 移除已发布的同名依赖库
                for d in models.Depend.objects.filter(name = depend.name, status = Status.Released.value):
                    d.delete();
                # 更新当前依赖库的状态
                depend.status = Status.Released.value;
                depend.save();
                result["requestTips"] =  f"依赖库【{did}，{depend.name}，{depend.file_key}，{depend.time}】成功发布！";
            elif examType == "delete":
                depend.delete();
                delText = "撤回";
                if depend.status == Status.Released.value:
                    delText = "下架";
                result["requestTips"] =  f"依赖库【{did}，{depend.name}，{depend.file_key}，{depend.time}】成功{delText}！";
                # 发送邮件通知
                sendMsgToAllMgrs(f"管理员【{userAuth.uid.name}】于{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}，{delText}了【{did}，{depend.name}，{depend.file_key}，{depend.time}】依赖库。");
        except Exception as e:
            _GG("Log").w(e);
            result["requestFailedTips"] = f"依赖库【{did}】发布/撤回/下架失败。";
    else:
        result["requestFailedTips"] = f"审核依赖库的信息不完整，请重新上传！";

# 删除除指定版本外的其他版本
def delOtherVers(exe, version):
    base_version = ".".join(version.split(".")[:2]);
    if len(models.ExeDetail.objects.filter(eid = exe, base_version = base_version, version = version)) > 0:
        for ptip in models.ExeDetail.objects.filter(eid = exe, base_version = base_version):
            if ptip.version != version:
                ptip.delete();
    else:
        _GG("Log").w(f"不存在指定版本【{version}】的依赖程序，故不能删除除此版本外的其他版本！");