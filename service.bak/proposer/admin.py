from django.contrib import admin
from proposer.models import Service,ServiceConfig,Hosts,PlayBooks,Log,Task
# Register your models here.
admin.site.register(Service)
admin.site.register(ServiceConfig)
admin.site.register(Hosts)
admin.site.register(PlayBooks)
admin.site.register(Log)
admin.site.register(Task)
