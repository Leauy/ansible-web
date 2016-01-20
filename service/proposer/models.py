from django.db import models
#coding:utf-8
# Create your models here.


class Environment(models.Model):
    id = models.AutoField(primary_key=True)        
    name = models.CharField(max_length=100)
    def __unicode__(self):
        return self.name

from django.contrib.auth.models import User
class Profile(models.Model):
    user = models.OneToOneField(User)
    environments = models.ManyToManyField(Environment)

    
class Service(models.Model):
    id = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=60)
    chinese_name = models.CharField(max_length=60)
    def __unicode__(self):
        return self.service_name

class ServiceConfig(models.Model):
    id = models.AutoField(primary_key=True)
    config_name = models.CharField(max_length=50)
    config_value = models.CharField(max_length=200,null=True)
    environment = models.ForeignKey(Environment)
    service = models.ForeignKey(Service)
    def __unicode__(self):
        return self.config_name

class Hosts(models.Model):
    id = models.AutoField(primary_key=True)
    ip = models.GenericIPAddressField()
    hostname = models.CharField(max_length=50)
    chinese_name = models.CharField(max_length=200)
    ansible_ssh_user = models.CharField(max_length=50)
    ansible_ssh_private_key_file = models.FileField(upload_to='ssh/')
    ansible_ssh_pass = models.CharField(max_length=50,null=True)
    environment = models.ForeignKey(Environment)
    services = models.ManyToManyField(Service)
    def __unicode__(self):
        return self.ip

class PlayBooks(models.Model):
    id = models.AutoField(primary_key=True)
    usages = models.CharField(max_length=50)
    playbook_file = models.FileField(upload_to='playbooks/')
    service = models.ForeignKey(Service)
    def __unicode__(self):
        return self.playbook_file.name

class Log(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=10000)
    operator = models.CharField(max_length=50,null=True,blank=True)
    operate_time = models.DateTimeField(auto_now_add=True)

class Task(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    playbook = models.ForeignKey(PlayBooks)
    environment = models.ForeignKey(Environment)
    hosts = models.ManyToManyField(Hosts)

class Config(models.Model):
    id = models.AutoField(primary_key=True)
    svn_version = models.CharField(max_length=50)
    hosts = models.ManyToManyField(Hosts)
    environment = models.ForeignKey(Environment)


