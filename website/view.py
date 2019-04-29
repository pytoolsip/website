from django.shortcuts import render;

def home(request):
    return render(request, "home.html", [
        {
            "name" : "工具名称",
            "category" : "工具类别",
            "tkey" : "ac6116b2555f703585a8b7abca84b1bf",
            "description" : "工具描述",
            "downloadCount" : 0,
            "score" : 0.0,
            "author" : "作者",
            "uploadTime" : "2019-04-29",
        },
    ]);