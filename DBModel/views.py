from django.shortcuts import render

from DBModel.models import Tool

# Create your views here.
def home(request):
    toolInfoList = Tool.objects.order_by('time');
    return render(request, "home.html", {
        "toolInfoList" : [{
            "name" : toolInfo.name,
            "category" : toolInfo.category,
            "tkey" : toolInfo.tkey,
            "description" : toolInfo.description,
            "downloadCount" : toolInfo.download or 0,
            "score" : toolInfo.score or 0.0,
            "author" :  toolInfo.uid,
            "uploadTime" :  toolInfo.time,
        } for toolInfo in toolInfoList],
    });