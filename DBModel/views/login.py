from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import django.utils.timezone as timezone
from django.http import JsonResponse

from DBModel import models

# 登陆页请求
@csrf_exempt
def login(request):
    result = {"isSuccess" : False};
    if not request.POST:
        return JsonResponse(result);
    try:
        user = None;
        if "uid" in request.POST:
            user = models.User.objects.get(id = request.POST["uid"]);
        elif "name" in request.POST and "password" in request.POST:
            user = models.User.objects.get(name = request.POST["name"], password = request.POST["password"]);
        if user:
            result = {
                "isSuccess" : True,
                "uid" : user.id,
                "name" : user.name,
                "email" : user.email,
            };
    except Exception as e:
        print(e);
    return JsonResponse(result);