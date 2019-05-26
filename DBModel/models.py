from django.db import models

class Collection(models.Model):
    uid = models.ForeignKey('User', models.DO_NOTHING, db_column='uid')
    tkey = models.ForeignKey('Tool', models.DO_NOTHING, db_column='tkey', to_field='tkey')

    class Meta:
        managed = False
        db_table = 'collection'


class Comment(models.Model):
    uid = models.ForeignKey('User', models.DO_NOTHING, db_column='uid')
    tkey = models.ForeignKey('Tool', models.DO_NOTHING, db_column='tkey', to_field='tkey')
    score = models.FloatField()
    content = models.TextField()
    time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'comment'


class Ptip(models.Model):
    id = models.IntegerField(primary_key=True)
    version = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    changelog = models.TextField()
    time = models.DateTimeField()
    download_count = models.IntegerField()
    download_type = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ptip'


class Tool(models.Model):
    uid = models.ForeignKey('User', models.DO_NOTHING, db_column='uid')
    tkey = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField()
    score = models.FloatField(blank=True, null=True)
    download = models.IntegerField(blank=True, null=True)
    time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tool'
        unique_together = (('id', 'tkey'),)


class ToolDetail(models.Model):
    tkey = models.ForeignKey(Tool, models.DO_NOTHING, db_column='tkey', to_field='tkey')
    version = models.CharField(max_length=255)
    ip_version = models.CharField(max_length=255)
    changelog = models.TextField()
    url = models.CharField(max_length=255)
    time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tool_detail'


class User(models.Model):
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'user'