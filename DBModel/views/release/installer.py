import django.utils.timezone as timezone;
from DBModel import models;

from utils import base_util;

from _Global import _GG;

from base import *

# 上传安装程序文件
def uploadInstaller(request, userAuth, result, isSwitchTab):
    if not isSwitchTab:
        saveInstaller(request, userAuth, result);
    # 返回线上版本数据
    result["onlineInfoList"] = getOlInstallerInfoList();

# 保存安装程序信息
def saveInstaller(request, userAuth, result):
    version, file_path, changelog = request.POST.get("version", None), request.FILES.get("file", None), request.POST.get("changelog", None);
    if version and file_path and changelog:
        # 保存程序详情
        vList = version.split(".");
        base_version = ".".join(vList[:2]);
        if base_util.verifyVersion(version, [installerInfo.version for installerInfo in models.Installer.objects.filter(base_version = base_version)]):
            models.Installer(version = version, file_path = file_path, base_version = base_version, changelog = changelog, time = timezone.now()).save();
            # 删除除指定版本外的其他版本
            delOtherVers(version);
            result["requestTips"] = f"安装程序文件【{version}】上传成功。";
        else:
            result["requestFailedTips"] = f"已存在更高的更新安装程序版本号，请修改版本号【{version}】后重试！";
    else:
        result["requestFailedTips"] = f"上传安装程序的信息不完整，请重新上传！";

# 获取线上信息列表
def getOlInstallerInfoList():
    installerList = models.Installer.objects.all().order_by('-time');
    if len(installerList) > 0:
        return [{
            "version" : installerInfo.version,
            "time" : installerInfo.time,
            "changelog" : installerInfo.changelog,
            "url" : installerInfo.file_path.url,
        } for installerInfo in installerList];
    return [];

# 删除除指定版本外的其他版本
def delOtherVers(version):
    base_version = ".".join(version.split(".")[:2]);
    if len(models.Installer.objects.filter(base_version = base_version, version = version)) > 0:
        for ptip in models.Installer.objects.filter(base_version = base_version):
            if ptip.version != version:
                ptip.delete();
    else:
        _GG("Log").w(f"不存在指定版本【{version}】的依赖程序，故不能删除除此版本外的其他版本！");