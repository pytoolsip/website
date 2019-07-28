from django.db import models
import os

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


class Exe(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        managed = False
        db_table = 'exe'

# 运行程序文件路径
def exe_directory_path(instance, filename):
    ext = os.path.splitext(filename)[1];
    return os.path.join("release", "exe", f"{instance.name}-{instance.version}.{ext}");
class ExeDetail(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.ForeignKey(Exe, models.DO_NOTHING, db_column='name')
    version = models.CharField(max_length=255)
    file_path = models.FileField(upload_to = exe_directory_path)
    changelog = models.TextField()
    time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'exe_detail'

# 平台脚本文件路径
def ptip_directory_path(instance, filename):
    ext = os.path.splitext(filename)[1];
    vList = instance.version.split(".");
    return os.path.join("release", "ptip", "script", ".".join(vList[:1]), f"{instance.version}.{ext}");
# 平台工程文件路径
def ptip_pj_directory_path(instance, filename):
    ext = os.path.splitext(filename)[1];
    vList = instance.version.split(".");
    return os.path.join("release", "ptip", "project", ".".join(vList[:1]), f"PyToolsIP-{instance.version}.{ext}");
class Ptip(models.Model):
    id = models.IntegerField(primary_key=True)
    version = models.CharField(max_length=255)
    file_path = models.FileField(upload_to = ptip_directory_path)
    changelog = models.TextField()
    time = models.DateTimeField()
    project_path = models.FileField(upload_to = ptip_pj_directory_path)
    download = models.IntegerField()
    base_version = models.CharField(max_length=255)
    update_version = models.CharField(max_length=255)

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


# 平台文件路径
def tool_directory_path(instance, filename):
    ext = os.path.splitext(filename)[1];
    vList = instance.version.split(".");
    return os.path.join("release", "tools", instance.tkey, ".".join(vList[:1]), f"{instance.version}.{ext}");
class ToolDetail(models.Model):
    tkey = models.ForeignKey(Tool, models.DO_NOTHING, db_column='tkey', to_field='tkey')
    version = models.CharField(max_length=255)
    ip_base_version = models.CharField(max_length=255)
    changelog = models.TextField()
    file_path = models.FileField(upload_to = tool_directory_path)
    time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tool_detail'


class User(models.Model):
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    authority = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'user'