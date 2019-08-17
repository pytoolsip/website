import os, json, subprocess;

pipPath = "pip";

# 获取依赖模块表
def getDependMods():
    modList = [];
    if not os.path.exists("depend.mod"):
        return modList;
    with open("depend.mod", "r") as f:
        for line in f.readlines():
            mod = line.strip();
            if mod not in modList:
                modList.append(mod);
    return modList;

# 获取已安装模块
def getInstalledMods():
    modList = [];
    ret = subprocess.check_output(f"{pipPath} freeze");
    for line in ret.decode().split("\n"):
        line = line.strip();
        if line:
            modList.append(line.split("==")[0]);
    return modList;

# 获取未安装模块
def getUninstalledMods():
    modList = getInstalledMods(); # 获取已安装模块
    unInstallMods = [];
    for mod in getDependMods():
        if mod not in modList:
            unInstallMods.append(mod);
    return unInstallMods;

# 安装模块
def installMods(mods):
    failedMods = [];
    for mod in mods:
        if subprocess.call(f"{pipPath} install {mod}") != 0:
            failedMods.append(mod);
    return failedMods;

# 构建依赖模块
def buildDepends():
    # 获取未安装模块
    unInstallMods = getUninstalledMods();

    # 打印未安装模块名称
    if len(unInstallMods) > 0:
        print("UnInstallMods:", unInstallMods)

    # 安装未安装模块
    failedMods = installMods(unInstallMods);
    if len(failedMods) > 0:
        print(f"{pipPath} install {failedMods} failed!");

if __name__ == '__main__':
    buildDepends();