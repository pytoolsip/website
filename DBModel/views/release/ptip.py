import django.utils.timezone as timezone;
from DBModel import models;
from utils import base_util;
from base import *;

import json;

from _Global import _GG;

# 上传平台脚本
def upload(request, user, result, isSwitchTab):
    if not isSwitchTab:
        # 保存平信息
        savePtip(request, result);
        # 修改更新版本
        updateBaseVer(request, result);
    # 返回线上版本数据
    result["onlineInfoList"].extend(getOlInfoList());
    # 返回所依赖的线上版本
    result["onlineExeInfoList"] = getOlExeInfoList();
    result["onlineEnvInfoList"] = getOlEnvInfoList();

# 审核平台
def examine(request, user, result, isSwitchTab):
    if not isSwitchTab and user.authority == 1:
        # 发布平台
        releasePtip(request, user, result);
    # 返回线上版本
    ptipList = models.Ptip.objects.filter(status = Status.Examing.value).order_by('time');
    if len(ptipList) > 0:
        result["onlineInfoList"] = [{
            "id" : ptipInfo.id,
            "version" : ptipInfo.version,
            "time" : ptipInfo.time,
            "changelog" : ptipInfo.changelog,
            "url" : ptipInfo.file_path.url,
        } for ptipInfo in ptipList];

# 获取依赖程序url的json
def getExeJson(exeList):
    exeJson = [];
    for name, version in json.loads(exeList):
        try:
            exe = models.Exe.objects.get(name = name);
            exeDetail = models.ExeDetail.objects.get(eid = exe, version = version);
            exeJson.append({"url" : exeDetail.file_path.url, "path" : exe.path});
        except Exception as e:
            _GG("Log").d(e);
    return json.dumps(exeJson);

# 获取依赖环境url的json
def getEnvJson(envList):
    envJson = [];
    for name in json.loads(envList):
        try:
            env = models.Depend.objects.get(name);
            envJson.append({"url" : env.file_path.url, "path" : env.path});
        except Exception as e:
            _GG("Log").d(e);
    return json.dumps(envJson);

# 保存平台信息
def savePtip(request, result):
    version, file_path, changelog = request.POST.get("version", None), request.FILES.get("file", None), request.POST.get("changelog", None);
    exeList, envList = request.POST.get("exeList", None), request.FILES.get("envList", None);
    if version and file_path and changelog and exeList and envList:
        vList = version.split(".");
        base_version = ".".join(vList[:1]);
        if base_util.verifyVersion(version, [ptipInfo.version for ptipInfo in models.Ptip.objects.filter(base_version = base_version)]):
            # 保存脚本文件
            p = models.Ptip(version = version, file_path = file_path, changelog = changelog, time = timezone.now(), base_version = base_version, update_version = base_version, status = Status.Uploading.value, exe_list = getExeJson(exeList), env_list = getEnvJson(envList));
            p.save();
            # 更新状态
            p.status = Status.Examing.value;
            p.save();
            result["requestTips"] = f"PTIP平台脚本【{version}】上传成功。";
        else:
            result["requestFailedTips"] = f"已存在更高的平台版本号，请修改版本号【{version}】后重试！";

# 保存平台信息
def updateBaseVer(request, result):
    pid, updateVer = request.POST.get("id", None), request.POST.get("updateVersion", None);
    if pid and updateVer:
        if len(models.Ptip.objects.filter(status = Status.Released.value, base_version = updateVer)) > 0:
            try:
                p = models.Ptip.objects.get(id = pid);
                p.update_version = updateVer;
                p.save();
                result["requestTips"] = f"PTIP平台版本【{request.POST['updateVersion']}】更新成功。";
            except Exception as e:
                _GG("Log").d(e);
                result["requestFailedTips"] = "所要更新版本的平台版本不存在，请刷新后重试！";
        else:
            result["requestFailedTips"] = "所选择的更新版本不存在，请重新选择！";

# 获取线上信息列表
def getOlInfoList():
    olInfoList = [];
    ptipList = models.Ptip.objects.filter(status = Status.Released.value).order_by('time');
    ptipList = ptipList.values("base_version").distinct().order_by('base_version');
    if len(ptipList) > 0:
        baseVerList = [];
        for ptipInfo in ptipList:
            baseVerList.insert(0, ptipInfo.base_version);
            olInfoList.append({
                "id" : ptipInfo.id,
                "version" : ptipInfo.version,
                "time" : ptipInfo.time,
                "changelog" : ptipInfo.changelog,
                "url" : ptipInfo.file_path.url,
                "update_version" : ptipInfo.update_version,
                "baseVerList" : baseVerList.copy(),
            });
    return olInfoList;

# 获取线上依赖程序信息
def getOlExeInfoList():
    olInfoList = [];
    for exe in models.Exe.objects.all():
        exeInfoList = models.ExeDetail.objects.filter(eid = exe).order_by('time');
        exeInfoList = exeInfoList.values("base_version").distinct().order_by('base_version');
        if len(exeInfoList) > 0:
            olInfoList.append({"name" : exe.name, "verlist" : [exeInfo.version for exeInfo in exeInfoList]});
    return olInfoList;

# 获取线上依赖黄金信息
def getOlEnvInfoList():
    envInfoList = models.Depend.objects.all().order_by('time');
    if len(envInfoList) > 0:
        return [{"name" : envInfo.name} for envInfo in envInfoList];
    return [];

# 发布平台
def releasePtip(request, user, result):
    pid, examType = request.POST.get("id", None), request.POST.get("examType", "");
    if pid and examType:
        try:
            p, msg, reasonMsg = models.Ptip.objects.get(id = pid), "", "";
            if examType == "release":
                p.status = Status.Released.value;
                # 删除除指定版本外的其他版本
                delOtherVers(p.version);
                msg = "发布";
            else:
                p.delete();
                msg, reasonMsg = "撤回", f"【撤回原因：{request.POST.get('reason', '无。')}】";
            result["requestTips"] = f"PTIP平台【{p.version}】成功{msg}。";
            # 发送邮件通知
            sendMsgToAllMgrs(f"管理员【{user.name}】于{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}，成功**{msg}**PTIP平台【{p.version}】。\n{reasonMsg}");
        except Exception as e:
            result["requestTips"] = f"平台【{p.version}】审核失败！";

# 删除除指定版本外的其他版本
def delOtherVers(version):
    base_version = ".".join(version.split(".")[:1]);
    if len(models.Ptip.objects.filter(status = Status.Released.value, base_version = base_version, version = version)) > 0:
        for ptip in models.Ptip.objects.filter(status = Status.Released.value, base_version = base_version):
            if ptip.version != version:
                ptip.delete();
    else:
        _GG("Log").w(f"不存在指定版本【{version}】的平台，故不能删除除此版本外的其他版本！");
