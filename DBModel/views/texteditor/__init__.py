from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from website import settings
from DBModel import models

import hashlib;
import os,sys;

from _Global import _GG;

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__));
sys.path.append(CURRENT_PATH);

try:
    import article;
except Exception as e:
	raise e;
finally:
	sys.path.remove(CURRENT_PATH);


# 富文本编辑请求
@csrf_exempt
def texteditor(request):
    return article.editArticle(request);