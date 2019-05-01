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
    version = models.CharField(max_length=255)
    score = models.FloatField()
    content = models.TextField()
    time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'comment'


class Tool(models.Model):
    uid = models.ForeignKey('User', models.DO_NOTHING, db_column='uid')
    tkey = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    common_version = models.CharField(max_length=255)
    description = models.TextField()
    url = models.CharField(max_length=255)
    time = models.DateTimeField()
    score = models.FloatField(blank=True, null=True)
    download = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tool'


class User(models.Model):
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'user'