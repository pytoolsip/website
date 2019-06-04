from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse

from DBModel import models

PtipKeyList = ["ptip_script", "ptip_exe", "update_exe"];

PtKeyList = ["pt_new_script", "pt_ol_script"];

def _verifyCategory_(category, isAddSlash = True):
    category = category.replace(" ", "");
    if len(category) > 0:
        if isAddSlash and category[-1] != "/":
            category += "/";
        elif category[-1] == "/":
            category = category[:-1];
    return category;

def _getMd5_(name, category):
    name = _verifyCategory_(category) + name;
    return hashlib.md5(name.encode("utf-8")).hexdigest();

# 上传平台脚本
def uploadPtipScript(request, user, result):
    if "isSwitchTab" not in request.POST:
        if request.POST.get("version", None) and request.POST.get("file", None) and request.POST.get("changelog", None):
            version = request.POST["version"];
            p = models.Ptip(version = version, file_path = request.POST["file"], changelog = request.POST["changelog"], time = timezone.now());
            p.save();
            result["requestTips"] = f"PTIP平台脚本【{version}】上传成功。";
    # 返回线上版本数据
    ptipList = models.Ptip.objects.order_by('time');
    if len(ptipList) > 0:
        result["onlineInfoList"] = [{
            "version" : ptipInfo.version,
            "time" : ptipInfo.time,
            "changelog" : ptipInfo.changelog,
            "url" : ptipInfo.file_path.url,
        } for ptipInfo in ptipList];

# 上传更新文件
def uploadUpdateFile(request, user, name, result):
    if "isSwitchTab" not in request.POST:
        if "version" in request.POST and "file" in request.POST and "changelog" in request.POST:
            version = request.POST["version"];
            try:
                ud = models.Update.objects.get(name = name);
                ud.version = version;
                ud.file_path = request.POST["file"];
                ud.changelog = request.POST["changelog"];
                ud.time = timezone.now();
            except Exception as e:
                ud = models.Update(name = name, version = version, file_path = request.POST["file"], changelog = request.POST["changelog"], time = timezone.now());
            ud.save();
            result["requestTips"] = f"更新文件【{version}】上传成功。";
    # 返回线上版本数据
    updateList = models.Update.objects.filter(name = name).order_by('time');
    if len(updateList) > 0:
        result["onlineInfoList"] = [{
            "version" : updateInfo.version,
            "time" : updateInfo.time,
            "changelog" : updateInfo.changelog,
            "url" : updateInfo.file_path.url,
        } for updateInfo in updateList];

# 上传新工具
def uploadNewTool(request, user, result):
    if "isSwitchTab" not in request.POST:
        for k in ["name", "category", "file", "description", "version", "ip_version"]:
            if k not in request.POST:
                result["requestFailedTips"] = "上传信息不完整，请重新选上传！";
                return;
        version = request.POST["version"];
        try:
            tool = models.Tool.objects.get(name = name, category = category);
            result["requestFailedTips"] = "已存在相同分类的工具名，请重新选上传！";
            return;
        except Exception as e:
            name, category = request.POST["name"], _verifyCategory_(request.POST["category"], False);
            tkey = _getMd5_(name, category);
            curTime = timezone.now();
            # 保存Tool
            tool = models.Tool(uid = user, tkey = tkey, name = name, category = category, description = request.POST["description"], time = curTime);
            tool.save();
            # 保存ToolDetail
            toolDetail = models.ToolDetail(tkey = tool, version = version, ip_version = request.POST["ip_version"], file_path = request.POST["file"], changelog = "初始版本。", time = curTime);
            toolDetail.save();
        result["requestTips"] = f"新工具【{version}】上传成功。";

# 更新线上工具
def uploadOlTool(request, user, tkey, result):
    if "isSwitchTab" not in request.POST:
        for k in ["file", "description", "changelog", "version", "ip_version"]:
            if k not in request.POST:
                result["requestFailedTips"] = "上传信息不完整，请重新选上传！";
                return;
        version = request.POST["version"];
        try:
            tool = models.Tool.objects.get(tkey = tkey);
            curTime = timezone.now();
            # 更新Tool
            tool.description = request.POST["description"];
            tool.time = curTime;
            tool.save();
            # 保存ToolDetail
            toolDetail = models.ToolDetail(tkey = tool, version = version, ip_version = request.POST["ip_version"], file_path = request.POST["file"], changelog = request.POST["changelog"], time = curTime);
            toolDetail.save();
            result["requestTips"] = f"线上工具新版本【{version}】上传成功。";
        except Exception as e:
            print(e);

# 后台管理页
@csrf_exempt
def manage(request, user, mkey):
    # 返回页面内容
    result = {
        "mkey" : mkey,
        "userInfo" : { # 用户信息
            "name":user.name,
            "pwd":user.password,
        },
        "isShowIpOption" : user.authority == 1, # 是否显示平台选项
        "requestTips" : "", # 请求提示
        "requestFailedTips" : "", # 请求失败提示
        "onlineInfoList" : [], # 线上信息列表
        "toolInfoData" : {"isUploadNew" : False, "isSearchNone" : False, "searchNoneTips" : ""}, # 工具信息数据
    };
    toolInfoData = result["toolInfoData"];
    if mkey == "ptip_script": # 更新平台脚本
        uploadPtipScript(request, user, result);
    elif mkey == "ptip_exe" or mkey == "update_exe": # 更新平台启动/更新程序
        uploadUpdateFile(request, user, mkey, result);
    elif mkey == "pt_new_script": # 上传新工具脚本
        uploadNewTool(request, user, result);
        toolInfoData["isUploadNew"] = True;
    elif mkey == "pt_ol_script": # 更新线上工具脚本
        tkey = request.POST.get("tkey", "");
        if tkey:
            # 返回线上版本数据
            toolInfoList = models.Tool.objects.filter(tkey = tkey, uid = user);
            if len(toolInfoList) > 0:
                # 从request.POST中获取上传数据
                uploadOlTool(request, user, tkey, result);
                # 返回线上版本数据
                baseInfo = toolInfoList[0];
                ptInfoList = models.ToolDetail.objects.filter(tkey = tkey).order_by('time');
                onlineInfoList = [{
                    "name" : baseInfo.name,
                    "category" : baseInfo.category,
                    "tkey" : baseInfo.tkey,
                    "description" : baseInfo.description,
                    "version" : ptInfo.version,
                    "time" : ptInfo.time,
                    "changelog" : ptInfo.changelog,
                    "url" : ptInfo.file_path.url,
                } for ptInfo in ptInfoList];
            else:
                toolInfoData["isSearchNone"] = True;
                toolInfoData["searchNoneTips"] = f"您未曾上传过ID为【{tkey}】工具，请重新搜索！";
        else:
            # 搜索结果数据
            s, searchNoneTips = request.POST.get("search", ""), "";
            if s:
                toolInfoList = models.Tool.objects.filter(name__icontains = s, uid = user.id);
                searchNoneTips = f"未搜索到名称为【{s}】的工具！";
            else:
                toolInfoList = models.Tool.objects.filter(uid = user.id);
                searchNoneTips = f"您还未曾上传过工具到线上，请上传新工具！";
            toolInfoData = {
                "isSearchNone" : len(toolInfoList) == 0,
                "searchNoneTips" : searchNoneTips,
                "infoList" : [{
                    "name" : toolInfo.name,
                    "category" : toolInfo.category,
                    "tkey" : toolInfo.tkey,
                    "description" : toolInfo.description,
                    "downloadCount" : toolInfo.download or 0,
                    "score" : toolInfo.score or 0.0,
                    "author" :  toolInfo.uid.name,
                    "uploadTime" :  toolInfo.time,
                } for toolInfo in toolInfoList],
            };
    return render(request, "manage/content.html", result);
