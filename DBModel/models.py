from django.db import models

# Create your models here.
class Tool(models.Model):
    id = models.IntegerField(primary_key=True);
    uid = models.IntegerField();
    tkey = models.CharField(max_length=255);
    category = models.CharField(max_length=255);
    name = models.CharField(max_length=255);
    version = models.CharField(max_length=255);
    common_version = models.CharField(max_length=255);
    description = models.TextField();
    time = models.DateTimeField();
    score = models.FloatField();
    download = models.IntegerField();
    
    class Meta:
        managed = False
        db_table = 'tool'