from django.views.decorators.csrf import csrf_exempt
import django.utils.timezone as timezone
from django.http import JsonResponse

from DBModel import models

import os,sys;

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__));
sys.path.append(CURRENT_PATH);

__all__ = ["home", "search", "detail", "userinfo", "release", "reqinfo", "toollist"];

try:
    from home import home;
    from search import search;
    from detail import detail;
    from userinfo import userinfo;
    from release import release;
    from reqinfo import reqinfo;
    from toollist import toollist;
    from texteditor import texteditor;

except Exception as e:
	raise e;
finally:
	sys.path.remove(CURRENT_PATH);