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


# 依赖库路径
def depend_lib_path(instance, filename):
    ext = os.path.splitext(filename)[1];
    return os.path.join("release", "depend", f"{instance.name}{ext}");
class Depend(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    file_path = models.FileField(upload_to = depend_lib_path)
    description = models.TextField()
    time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'depend'


class Exe(models.Model):
    name = models.CharField(max_length=255, unique=True)
    path = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'exe'


# 运行程序文件路径
def exe_directory_path(instance, filename):
    ext = os.path.splitext(filename)[1];
    return os.path.join("release", "exe", instance.eid.name, f"{instance.eid.name}_{instance.version}{ext}");
class ExeDetail(models.Model):
    eid = models.ForeignKey(Exe, models.DO_NOTHING, db_column='eid')
    version = models.CharField(max_length=255)
    file_path = models.FileField(upload_to = exe_directory_path)
    base_version = models.CharField(max_length=255)
    changelog = models.TextField()
    time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'exe_detail'


# 安装程序文件路径
def installer_directory_path(instance, filename):
    ext = os.path.splitext(filename)[1];
    return os.path.join("release", "installer", f"pytoolsip_installer_{instance.version}{ext}");
class Installer(models.Model):
    id = models.IntegerField(primary_key=True)
    version = models.CharField(max_length=255)
    changelog = models.CharField(max_length=255)
    file_path = models.FileField(upload_to = installer_directory_path)
    base_version = models.CharField(max_length=255)
    time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'installer'


# 平台脚本文件路径
def ptip_directory_path(instance, filename):
    ext = os.path.splitext(filename)[1];
    vList = instance.version.split(".");
    return os.path.join("release", "ptip", "script", ".".join(vList[:2]), f"ptip_{instance.version}{ext}");
class Ptip(models.Model):
    id = models.IntegerField(primary_key=True)
    version = models.CharField(max_length=255)
    file_path = models.FileField(upload_to = ptip_directory_path)
    changelog = models.TextField()
    time = models.DateTimeField()
    base_version = models.CharField(max_length=255)
    update_version = models.CharField(max_length=255)
    status = models.IntegerField()
    exe_list = models.TextField()
    env_list = models.TextField()

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
    return os.path.join("release", "tools", instance.tkey, ".".join(vList[:2]), f"{instance.tkey}_{instance.version}{ext}");
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


class ToolExamination(models.Model):
    id = models.IntegerField(primary_key=True)
    uid = models.ForeignKey('User', models.DO_NOTHING, db_column='uid')
    tkey = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    description = models.TextField()
    version = models.CharField(max_length=255)
    ip_base_version = models.CharField(max_length=255)
    changelog = models.TextField()
    file_path = models.FileField(upload_to = tool_directory_path)
    time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tool_examination'


class User(models.Model):
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    authority = models.IntegerField()
    salt = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = 'user'