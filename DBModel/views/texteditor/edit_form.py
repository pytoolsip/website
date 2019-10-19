from django.forms import CharField, ModelForm

from DBModel import models

class ToolForm(ModelForm):
    class Meta:
        model = models.Tool
        fields = ["detail"]

class ArticleForm(ModelForm):
    class Meta:
        model = models.Article
        fields = ["title", "thumbnail", "content"]