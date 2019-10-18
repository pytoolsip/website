from django.forms import ModelForm
from django.shortcuts import render

from DBModel import models

class ArticleForm(ModelForm):
    class Meta:
        model = models.Article
        fields = ["title", "thumbnail", "content"]
    

def editArticle(request):
    return render(request, "texteditor/edit_article.html", {"form" : ArticleForm()});