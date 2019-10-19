from django.shortcuts import render

from DBModel import models

def edit(request):
    return HttpResponse("你所访问的页面不存在", status=404);