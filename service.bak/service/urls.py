from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'service.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^proposer/tasks/(?P<id>\d+)/$','proposer.views.tasks'),

    url(r'^proposer/showPower/$','proposer.views.showPower'),
    #url(r'^proposer/modifyPower/(?P<id>\d+)/$','proposer.views.modifyPower'),
    url(r'^proposer/changeEnvironment/(?P<envir_id>\d+)/$','proposer.views.changeEnvironment'),

    url(r'^proposer/showLog/$','proposer.views.showLog'),
    url(r'^$', 'proposer.views.index', name='index'),
    url(r'proposer/index','proposer.views.index'),

    url(r'^proposer/login/$','proposer.views.login'),
    url(r'^proposer/logout/$','proposer.views.logout'),
    url(r'^proposer/changepwd/$','proposer.views.changepwd'),
    url(r'^proposer/addUser/$','proposer.views.addUser'),


#environment
    url(r'^proposer/showEnvironment/$','proposer.views.showEnvironment'),
    url(r'^proposer/addEnvironment/$','proposer.views.addEnvironment'),
    url(r'^proposer/modifyEnvironment/(?P<id>\d+)/$','proposer.views.modifyEnvironment'),
    url(r'^proposer/deleteEnvironment/(?P<id>\d+)/$','proposer.views.deleteEnvironment'),
#service
    url(r'^proposer/showService/$','proposer.views.showService'),
    url(r'^proposer/addService/$','proposer.views.addService'),
    url(r'^proposer/modifyService/(?P<id>\d+)/$','proposer.views.modifyService'),
    url(r'^proposer/deleteService/(?P<id>\d+)/$','proposer.views.deleteService'),
#serviceconfig
    url(r'^proposer/showServiceConfig/$','proposer.views.showServiceConfig'),
    url(r'^proposer/addServiceConfig/$','proposer.views.addServiceConfig'),
    url(r'^proposer/modifyServiceConfig/(?P<id>\d+)/$','proposer.views.modifyServiceConfig'),
    url(r'^proposer/deleteServiceConfig/(?P<id>\d+)/$','proposer.views.deleteServiceConfig'),

#hosts
    url(r'^proposer/showHosts/$','proposer.views.showHosts'),
    url(r'^proposer/addHosts/$','proposer.views.addHosts'),
    url(r'^proposer/modifyHosts/(?P<id>\d+)/$','proposer.views.modifyHosts'),
    url(r'^proposer/deleteHosts/(?P<id>\d+)/$','proposer.views.deleteHosts'),

#playbooks
    url(r'^proposer/showPlayBooks/$','proposer.views.showPlayBooks'),
    url(r'^proposer/addPlayBooks/$','proposer.views.addPlayBooks'),
    url(r'^proposer/modifyPlayBooks/(?P<id>\d+)/$','proposer.views.modifyPlayBooks'),
    url(r'^proposer/deletePlayBooks/(?P<id>\d+)/$','proposer.views.deletePlayBooks'),
#task
    url(r'^proposer/showTask/$','proposer.views.showTask'),
    url(r'^proposer/addTask/$','proposer.views.addTask'),
    url(r'^proposer/modifyTask/(?P<id>\d+)/$','proposer.views.modifyTask'),
    url(r'^proposer/deleteTask/(?P<id>\d+)/$','proposer.views.deleteTask'),
#task execute
    url(r'^proposer/executeTask/(?P<id>\d+)/$','proposer.views.executeTask'),
#config.yaml
    url(r'^proposer/makeConfigFile/$','proposer.views.makeConfigFile'),

#hosts file
    url(r'^proposer/makeHostsFile/$','proposer.views.makeHostsFile'),

    url(r'^static/(?P<path>.*)$','django.views.static.serve',),

    url(r'^admin/', include(admin.site.urls)),
)
