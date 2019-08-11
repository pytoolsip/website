import django.utils.timezone as timezone;
from DBModel import models;

from utils import base_util;

from _Global import _GG;

# 上传新工具
def uploadNew(request, user, result, isSwitchTab):
    if not isSwitchTab:
        file_path = request.FILES.get("file", None);
        name, category, description, version, ip_base_version = request.POST.get("name", None), request.POST.get("category", None), request.POST.get("description", None), request.POST.get("version", None), request.POST.get("ip_base_version", None);
        if file_path and name and category and description and version and ip_base_version:
            try:
                models.Tool.objects.get(name = name, category = category);
                models.ToolExamination.objects.get(name = name, category = category);
                result["requestFailedTips"] = "已存在相同分类的工具名，请重新上传！";
                return;
            except Exception as e:
                category = base_util._verifyCategory_(category, False);
                tkey = base_util._getMd5_(name, category);
                # 保存ToolExamination
                tool = models.ToolExamination(uid = user, tkey = tkey, name = name, category = category, description = description,
                version = version, ip_base_version = ip_base_version, file_path = file_path, changelog = "初始版本。", time = timezone.now());
                tool.save();
            result["requestTips"] = f"新工具【{tkey}， {version}】上传成功。";
        else:
            result["requestFailedTips"] = "上传信息不完整，请重新上传！";
    result["olIPBaseVerList"] = getOlIPBaseVerList();

# 更新线上工具
def uploadOl(request, user, tkey, result, isSwitchTab):
    try:
        tool = models.Tool.objects.get(tkey = tkey, uid = user);
        if not isSwitchTab:
            # 保存线上工具的更新信息
            saveOl(request, user, tool, result);
        # 获取线上信息
        result["onlineInfoList"] = getOnlineInfoList(tool);
        result["baseToolInfo"] = {
            "name" : tool.name,
            "category" : tool.category,
            "tkey" : tool.tkey,
            "description" : tool.description,
        };
        result["olIPBaseVerList"] = getOlIPBaseVerList();
    except Exception as e:
        _GG("Log").d(e);
        result["isSearchNone"] = True;
        result["searchNoneTips"] = f"您未曾发布过ID为【{tkey}】工具，请重新搜索！";

# 保存线上工具的更新信息
def saveOl(request, user, tool, result):
    file_path = request.FILES.get("file", None);
    changelog, description, version, ip_base_version = request.POST.get("changelog", None), request.POST.get("description", None), request.POST.get("version", None), request.POST.get("ip_base_version", None);
    if file_path and changelog and description and version and ip_base_version:
        if checkHasUnExamination(version):
            result["requestFailedTips"] = f"存在审核中的工具版本号，需撤回审核中的版本【{version}】后，才能发布新版本！";
        else:
            if base_util.verifyVersion(version, [te.version for te in models.ToolExamination.objects.all()]) and verifyVersion(version, [td.version for td in models.ToolDetail.objects.all()]):
                try:
                    # 保存ToolExamination
                    t = models.ToolExamination(uid = tool.uid, tkey = tool.tkey, name = tool.name, category = tool.category, description = description,
                    version = version, ip_base_version = ip_base_version, file_path = file_path, changelog = changelog, time = timezone.now());
                    t.save();
                    result["requestTips"] = f"线上工具新版本【{tool.tkey}， {version}】上传成功。";
                except Exception as e:
                    _GG("Log").d(e);
            else:
                result["requestFailedTips"] = f"已存在更高的工具版本号，请修改版本号【{version}】后重试！";
    else:
        result["requestFailedTips"] = "上传信息不完整，请重新上传！";

# 获取线上平台基础版本
def getOlIPBaseVerList():
    ptipList =  models.Ptip.objects.all().order_by('time');
    return ptipList.values("base_version").distinct();

# 获取线上信息列表
def getOnlineInfoList(baseInfo):
    ptInfoList = models.ToolDetail.objects.filter(tkey = baseInfo.tkey).order_by('time');
    ptInfoList = ptInfoList.values("base_version").distinct();
    return [{
        "name" : baseInfo.name,
        "category" : baseInfo.category,
        "tkey" : baseInfo.tkey,
        "description" : baseInfo.description,
        "version" : ptInfo.version,
        "time" : ptInfo.time,
        "changelog" : ptInfo.changelog,
        "url" : ptInfo.file_path.url,
    } for ptInfo in ptInfoList];

# 搜索工具信息数据
def searchTool(result, searchType, searchText, uid):
    searchNoneTips = "";
    if searchType == "name":
        toolInfoList = models.Tool.objects.filter(name__icontains = searchText, uid = uid);
        searchNoneTips = f"您未发布过名称包含为【{searchText}】工具，请重新搜索！";
    elif searchType == "tkey":
        toolInfoList = models.Tool.objects.filter(tkey = searchText, uid = uid);
        searchNoneTips = f"您未曾发布过ID为【{searchText}】工具，请重新搜索！";
    else:
        toolInfoList = models.Tool.objects.filter(uid = uid);
        searchNoneTips = f"您还未曾发布过工具到线上，请先上传新工具！";
    # 设置返回数据
    result["searchType"] = searchType;
    result["searchText"] = searchText;
    result["isSearchNone"] = len(toolInfoList) == 0;
    result["searchNoneTips"] = searchNoneTips;
    result["toolInfoList"] = [{
        "name" : toolInfo.name,
        "category" : toolInfo.category,
        "tkey" : toolInfo.tkey,
        "description" : toolInfo.description,
        "downloadCount" : toolInfo.download or 0,
        "score" : toolInfo.score or 0.0,
        "author" :  toolInfo.uid.name,
        "uploadTime" :  toolInfo.time,
    } for toolInfo in toolInfoList];

# 审核工具
def examTool(request, user, result, isSwitchTab):
    if not isSwitchTab:
        examType, tid = request.POST.get("examType", None), request.POST.get("id", None);
        if examType and tid:
            try:
                t, msg, reasonMsg = models.ToolExamination.objects.get(id = tid), "", "";
                # 判断用户权限
                if user.authority == 0 and t.uid.id != user.id:
                    result["requestFailedTips"] = f"您没有权限审核工具【{t.tkey}，{t.version}】！";
                    return;
                if examType == "release":
                    # 发布工具
                    releaseTool(t);
                    msg = "发布";
                else:
                    msg, reasonMsg = "撤回", f"【撤回原因：{request.POST.get('reason', '无。')}】";
                t.delete(); # 移除审核中的工具信息
                result["requestTips"] = f"工具【{t.tkey}，{t.version}】成功{msg}。";
                # 发送邮件通知
                userIdentity, opMsg = "用户", "完成";
                if user.authority == 1:
                    userIdentity, opMsg = "管理员", "被管理员";
                sendMsgToAllMgrs(f"{userIdentity}【{user.name}】于{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}，成功**{msg}**工具【{t.tkey}，{t.version}】。");
                sendToEmails(f"您在{t.time.strftime('%Y-%m-%d %H:%M:%S')}上传的工具【{t.tkey}，{t.version}】，于{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}**{msg}**。\n{reasonMsg}", [t.uid.email]);
            except Exception as e:
                result["requestFailedTips"] = f"未找到工具【{t.tkey}，{t.version}】，审核失败！";
    # 返回线上版本
    result["onlineInfoList"] = getToolExamination();

# 发布工具
def releaseTool(t):
    try:
        tool = models.Tool.objects.get(tkey = t.tkey);
        # 更新Tool
        tool.description = t.description;
        tool.time = t.time;
        tool.save();
    except Exception as e:
        # 保存Tool
        tool = models.Tool(uid = t.uid, tkey = t.tkey, name = t.name, category = t.category, description = t.description, time = t.time);
        tool.save();
    # 保存ToolDetail
    toolDetail = models.ToolDetail(tkey = tool, version = t.version, ip_base_version = t.ip_base_version, file_path = t.file_path, changelog = t.changelog, time = t.time);
    toolDetail.save();
    # 删除除指定版本外的其他版本
    delOtherVers(t.version, t.ip_base_version);

# 获取所有审核的工具信息
def getToolExamination():
    toolList = models.ToolExamination.objects.all().order_by('time');
    if len(toolList) > 0:
        return [{
            "id" : toolInfo.id,
            "name" : toolInfo.name,
            "category" : toolInfo.category,
            "tkey" : toolInfo.tkey,
            "description" : toolInfo.description,
            "version" : toolInfo.version,
            "time" : toolInfo.time,
            "changelog" : toolInfo.changelog,
            "url" : toolInfo.file_path.url,
        } for toolInfo in toolList];
    return [];

# 审核线上工具
def examOlTool(request, user, result, isSwitchTab):
    if not isSwitchTab and user.authority == 1:
        examType, tid = request.POST.get("examType", None), request.POST.get("id", None);
        if examType and tid:
            try:
                t = models.ToolDetail.objects.get(id = tid);
                if request.POST["examType"] == "delete":
                    t.delete();
                    if len(models.ToolDetail.objects.filter(tkey = t.tkey)) == 0:
                        t.tkey.delete();
                    result["requestTips"] = f"工具【{t.tkey}，{t.version}】下架成功。";
                    # 发送邮件通知
                    sendMsgToAllMgrs(f"管理员【{user.name}】于{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}，成功**下架**工具【{t.tkey}，{t.version}】。");
                    exMsg = f"【下架原因：{request.POST.get('reason', '无。')}】";
                    sendToEmails(f"您在{t.time.strftime('%Y-%m-%d %H:%M:%S')}上传的工具【{t.tkey}，{t.version}】，于{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}进行了**下架**。\n{exMsg}");
            except Exception as e:
                result["requestFailedTips"] = f"工具【{t.tkey}，{t.version}】审核失败！";
    # 设置权限
    result["isReleased"] = True;
    # 返回线上版本
    toolList = models.Tool.objects.all().order_by('time');
    for toolInfo in toolList:
        result["onlineInfoList"].extend(getOnlineInfoList(toolInfo));

# 检测是否存在有未审核的版本号
def checkHasUnExamination(version):
    return len(models.ToolExamination.objects.filter(version = version)) > 0;

# 删除除指定版本外的其他版本
def delOtherVers(version, ip_base_version):
    if len(models.ToolDetail.objects.filter(version = version, ip_base_version = ip_base_version)) > 0:
        for t in models.ToolDetail.objects.filter(ip_base_version = ip_base_version):
            if t.version != version:
                t.delete();
    else:
        _GG("Log").w(f"不存在指定平台版本【{ip_base_version}】的工具版本【{version}】，故不能删除除此工具版本外的其他版本！");