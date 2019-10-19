from django.shortcuts import render
from django.http import JsonResponse,HttpResponse

from DBModel import models

from edit_form import ToolForm;

from _Global import _GG;

def edit(request, userAuth):
    tool = getToolInfoByTKey(userAuth, request.GET.get("tkey", ""));
    if not tool:
        return HttpResponse("你所访问的页面不存在", status=404);
    if "detail" in request.POST:
        tool.detail = request.POST["detail"];
        tool.save();
        return render(request, "texteditor/edit_tool_detail.html", {
            "tkey" : tool.tkey,
            "name" : tool.name,
            "category" : tool.category,
            "description" : tool.description,
            "detail" : tool.detail,
            "tips" : "工具详情更新成功。",
        });
    return render(request, "texteditor/edit_tool_detail.html", {
        "tkey" : tool.tkey,
        "name" : tool.name,
        "category" : tool.category,
        "description" : tool.description,
        "detail" : tool.detail,
        "form" : ToolForm(),
    });

def getToolInfoByTKey(userAuth, tkey):
    try:
        return models.Tool.objects.get(tkey = tkey, uid = userAuth.uid);
    except Exception as e:
        _GG("Log").w(e);
    try:
        return models.ToolExamination.objects.get(tkey = tkey, uid = userAuth.uid);
    except Exception as e:
        _GG("Log").w(e);
    return None;