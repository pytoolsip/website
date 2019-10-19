from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from website import settings
from DBModel import models

import userinfo;

import hashlib;
import os,sys;

from _Global import _GG;

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__));
sys.path.append(CURRENT_PATH);

try:
    import article_editor;
    import tool_editor;
except Exception as e:
	raise e;
finally:
	sys.path.remove(CURRENT_PATH);


# 富文本编辑请求
@csrf_exempt
def texteditor(request):
    # 获取登陆玩家
    uname, upwd = request.POST.get("uname", ""), request.POST.get("upwd", "");
    userAuth = userinfo.getLoginUserAuth(uname, upwd);
    if not userAuth:
        # 返回登陆页面信息
        ret = {"HOME_URL": settings.HOME_URL};
        if uname and upwd:
            ret = {"requestFailedTips" : "登陆信息已过期！"};
        return render(request, "release/login.html", ret);
    # 根据不同请求，返回不同内容
    ek = request.GET.get("ek", "");
    if ek == "tool":
        return tool_editor.edit(request, userAuth);
    elif ek == "article":
        return article_editor.edit(request, userAuth);
    return HttpResponse("你所访问的页面不存在", status=404);