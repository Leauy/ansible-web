#coding:utf-8
from django.shortcuts import render,render_to_response
from django import forms
from django.forms import ModelForm
from django.http import HttpResponse,HttpResponseRedirect
from bootstrap_toolkit.widgets import BootstrapDateInput, BootstrapTextInput, BootstrapUneditableInput
# Create your views here.
from proposer.models import Service,ServiceConfig,Hosts,PlayBooks,Log,Task,Config,Environment,Profile
from django.template.context import RequestContext


from django.contrib.auth.models import User 
from django.contrib import auth  
from django.contrib import messages 
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required  

#读取service.conf 配置文件，获取保存用户上传的文件目录路径
import os
import ConfigParser
config = ConfigParser.ConfigParser()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
config.read(os.path.join(BASE_DIR, 'service.conf'))
MEDIA_ROOT = config.get('db','media_root')
#读取service.conf 配置文件，获取保存用户上传的文件目录路径

#分页模块
from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger
def my_pagination(request, queryset, display_amount=10, after_range_num = 5,bevor_range_num = 4):
    #按参数分页
    paginator = Paginator(queryset, display_amount)
    try:
        #得到request中的page参数
        page =int(request.GET.get('page'))
    except:
        #默认为1
        page = 1
    try:
        #尝试获得分页列表
        objects = paginator.page(page)
    #如果页数不存在
    except EmptyPage:
        #获得最后一页
        objects = paginator.page(paginator.num_pages)
    #如果不是一个整数
    except:
        #获得第一页
        objects = paginator.page(1)
    #根据参数配置导航显示范围
    if page >= after_range_num:
        page_range = paginator.page_range[page-after_range_num:page+bevor_range_num]
    else:
        page_range = paginator.page_range[0:page+bevor_range_num]
    return objects,page_range
#分页模块

import logging
logger = logging.getLogger(__name__)
from django.utils import timezone

class ConfigForm(ModelForm):
    svn_version = forms.CharField(
        required=False,
        label=u"svn版本号",
        widget=forms.TextInput(
            attrs={
                'placeholder':u'svn_版本号',
            }
        )
    )
    class Meta:
        model = Config
        fields = '__all__'

#主页
def index(request):
    if request.user.username == '':
        return HttpResponseRedirect("/proposer/login/")
    else:
        return render_to_response('index.html',RequestContext(request,{'user':request.user,}))

#用户登录模块
class LoginForm(forms.Form):  
    username = forms.CharField(  
        required=True,  
        label=u"用户名",  
        error_messages={'required': u'请输入用户名'},  
        widget=forms.TextInput(  
            attrs={  
                'placeholder':u"用户名",  
            }  
        ),  
    )      
    password = forms.CharField(  
        required=True,  
        label=u"密码",  
        error_messages={'required': u'请输入密码'},  
        widget=forms.PasswordInput(  
            attrs={  
                'placeholder':u"密码",  
            }  
        ),  
    )     
    def clean(self):  
        if not self.is_valid():  
            raise forms.ValidationError(u"用户名和密码为必填项")  
        else:  
            cleaned_data = super(LoginForm, self).clean()

class ChangepwdForm(forms.Form):  
    oldpassword = forms.CharField(  
        required=True,  
        label=u"原密码",  
        error_messages={'required': u'请输入原密码'},  
        widget=forms.PasswordInput(  
            attrs={  
                'placeholder':u"原密码",  
            }  
        ),  
    )   
    newpassword1 = forms.CharField(  
        required=True,  
        label=u"新密码",  
        error_messages={'required': u'请输入新密码'},  
        widget=forms.PasswordInput(  
            attrs={  
                'placeholder':u"新密码",  
            }  
        ),  
    )  
    newpassword2 = forms.CharField(  
        required=True,  
        label=u"确认密码",  
        error_messages={'required': u'请再次输入新密码'},  
        widget=forms.PasswordInput(  
            attrs={  
                'placeholder':u"确认密码",  
            }  
        ),  
     )  
    def clean(self):  
        if not self.is_valid():  
            raise forms.ValidationError(u"所有项都为必填项")  
        elif self.cleaned_data['newpassword1'] != self.cleaned_data['newpassword2']:  
            raise forms.ValidationError(u"两次输入的新密码不一样")  
        else:  
            cleaned_data = super(ChangepwdForm, self).clean()  
        return cleaned_data 

class UserForm(forms.Form):
    username = forms.CharField(  
        required=True,  
        label=u"用户名",  
        error_messages={'required': u'请输入用户名'},  
        widget=forms.TextInput(  
            attrs={  
                'placeholder':u"用户名",  
            }  
        ),  
    )      
    password = forms.CharField(  
        required=True,  
        label=u"密码",  
        error_messages={'required': u'请输入密码'},  
        widget=forms.PasswordInput(  
            attrs={  
                'placeholder':u"密码",  
            }  
        ),  
    )    
    def clean(self):  
        if not self.is_valid():  
            raise forms.ValidationError(u"所有项都为必填项")  
        else:  
            cleaned_data = super(UserForm, self).clean()  
        return cleaned_data 


def login(request):  
    if request.method == 'GET':  
        form = LoginForm()  
        return render_to_response('login.html', RequestContext(request, {'form': form,}))  
    else:  
        form = LoginForm(request.POST)  
        if form.is_valid():  
            username = request.POST.get('username', '')  
            password = request.POST.get('password', '')  
            user = auth.authenticate(username=username, password=password)  
            if user is not None and user.is_active:  
                auth.login(request, user)  
                return HttpResponseRedirect('/') 
            else:  
                return render_to_response('login.html', RequestContext(request, {'form': form,'password_is_wrong':True}))  
        else:  
            return render_to_response('login.html', RequestContext(request, {'form': form,}))


  
def logout(request):  
    auth.logout(request)  
    return HttpResponseRedirect("/proposer/login/")  

 
def changepwd(request):  
    user = request.user
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    if request.method == 'GET':  
        form = ChangepwdForm()  
        return render_to_response('changepwd.html', RequestContext(request, {'form': form,}))  
    else:  
        form = ChangepwdForm(request.POST)  
        if form.is_valid():  
            username = request.user.username  
            oldpassword = request.POST.get('oldpassword', '')  
            user = auth.authenticate(username=username, password=oldpassword)  
            if user is not None and user.is_active:  
                newpassword = request.POST.get('newpassword1', '')  
                user.set_password(newpassword)  
                user.save()  
                return render_to_response('index.html', RequestContext(request,{'changepwd_success':True}))  
            else:  
                return render_to_response('changepwd.html', RequestContext(request, {'form': form,'oldpassword_is_wrong':True}))  
        else:  
            return render_to_response('changepwd.html', RequestContext(request, {'form': form,})) 

def addUser(request):
    if request.method == 'GET':
        form = UserForm()
        return render_to_response('addUser.html',RequestContext(request,{'form':form,}))
    else:
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = User.objects.create_user(username,'',password)
            user.is_staff = True
            user.is_active = True
            #user.is_superuser = True
            user.save()
            Profile.objects.create(user=user)
            
            return HttpResponseRedirect('/proposer/login/')
        else:
            form = UserForm()
            return render_to_response('addUser.html',RequestContext(request,{'form':form,}))
#用户登录模块

#搜索模块
class SearchForm(forms.Form):
    search_text = forms.ModelChoiceField(queryset=Service.objects.all(),required=False)
#ce shi huanjing 

class IPSearchForm(forms.Form):
    search_text = forms.CharField(
        required=False,
        label=u"ip",
        widget = forms.TextInput(
    	    attrs = {
    		    'placeholder':u'请输入ip',
    		}
	    ),
    )

class operateSearchForm(forms.Form):
    search_text = forms.CharField(
        required=False,
        label=u"操作名",
        widget = forms.TextInput(
            attrs = {
                'placeholder':u'请输入操作名',
            }
        ),
    )
        
#搜索模块

#Service模块
class ServiceForm(ModelForm):
    service_name = forms.CharField(  
        required=True,  
        label= u"服务名:",  
        error_messages={'required': u'请输入服务名'},  
        widget=forms.TextInput(  
            attrs={  
                'placeholder':u"服务名",  
            }  
        ),  
    )    
    chinese_name = forms.CharField(  
        required=True,  
        label= u"中文名:",  
        error_messages={'required': u'请输入中文名'},  
        widget=forms.TextInput(  
            attrs={  
                'placeholder':u"中文名",  
            }  
        ),  
    )       
    class Meta:
        model = Service
        fields = "__all__" 

def showService(request):
    user = request.user
    sef = ServiceForm()
    if user.username == '':
        form = LoginForm()  
        return HttpResponseRedirect("/proposer/login/")

    servAll = Service.objects.all()
    objects, page_range = my_pagination(request, servAll)
    sf = SearchForm()
    if request.method == 'GET': 
        return render_to_response('showService.html',RequestContext(request,{'objects':objects,'sf':sf,'page_range':page_range,'sef':sef,}))
    else:
        sf = SearchForm(request.POST)
        if sf.is_valid():
            objects = Service.objects.filter(service_name__contains=sf.cleaned_data['search_text']) 
            return render_to_response('showService.html',RequestContext(request,{'objects':objects,'sf':sf,'sef':sef,}))
        else:
            return render_to_response('showService.html',RequestContext(request,{'objects':objects,'page_range':page_range,'sf':sf,'sef':sef,}))



def addService(request):
    user = request.user
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    now = timezone.now().strftime("%Y-%m-%d")
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    if request.method == 'GET':
        sef =ServiceForm()
        return render_to_response('addService.html',RequestContext(request,{'sef':sef,}))
    else:
        sef = ServiceForm(request.POST)
        if sef.is_valid():
            service_name = sef.cleaned_data['service_name']
            chinese_name = sef.cleaned_data['chinese_name']
            Service.objects.create(service_name=service_name,chinese_name=chinese_name)
            
            log = Log()
            log.name = "<strong>add_Service:</strong>"
            log.description = "<strong>service_name:%s <br> chinese_name:%s</strong>" % (service_name,chinese_name)
            log.operator = user.username
            log.operate_time = now
            log.save()
            return HttpResponseRedirect('/proposer/showService/')
        else:
            return render_to_response('addService.html',RequestContext(request,{'sef':sef,}))  


def modifyService(request,id):
    user = request.user
    if user.username == '':
        form = LoginForm()  
        return HttpResponseRedirect("/proposer/login/")
        
    now = timezone.now().strftime("%Y-%m-%d")
    service = Service.objects.get(id=id)
    if request.method == 'GET':
        sef =ServiceForm(initial={'service_name':service.service_name,'chinese_name':service.chinese_name,})
        return render_to_response('modifyService.html',RequestContext(request,{'sef':sef,}))
    else:
        sef = ServiceForm(request.POST)
        if sef.is_valid():
            service_name = sef.cleaned_data['service_name']
            chinese_name = sef.cleaned_data['chinese_name']
            log = Log()
            log.name = "<strong>modify_Service:</strong>"
            log.description="<strong>service_name: %s to %s <br> chinese_name: %s to %s</strong>" %(service.service_name,service_name,service.chinese_name,chinese_name)
            log.operator = user.username
            log.operate_time = now
            log.save()

            service.service_name = service_name
            service.chinese_name = chinese_name
            service.save()
            return HttpResponseRedirect('/proposer/showService/')
        else:
            return render_to_response('modifyService.html',RequestContext(request,{'sef':sef,}))


def deleteService(request,id):
    user = request.user
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    now = timezone.now().strftime("%Y-%m-%d")
    service = Service.objects.get(id=id)
    
    log = Log()
    log.name = "<strong>delete_Service:</strong>"
    log.description = u"<strong>service_name:%s <br> chinese_name：%s</strong>" % (service.service_name,service.chinese_name)
    log.operator = user.username
    log.operate_time = now
    log.save()
   
    service.delete()
    return HttpResponseRedirect('/proposer/showService/')
 #Service模块 

#Environment模块
class EnvironmentForm(ModelForm):
    name = forms.CharField(  
        required=True,  
        label= u"环境名:",  
        error_messages={'required': u'请输入环境名'},  
        widget=forms.TextInput(  
            attrs={  
                'placeholder':u"环境名",  
            }  
        ),  
    )        
    class Meta:
        model = Environment
        fields = "__all__" 

def showEnvironment(request):
    user = request.user
    ef = EnvironmentForm()
    if user.username == '': 
        return HttpResponseRedirect("/proposer/login/")

    EnvirAll = Environment.objects.all()
    objects, page_range = my_pagination(request, EnvirAll)
    return render_to_response('showEnvironment.html',RequestContext(request,{'objects':objects,'ef':ef,'page_range':page_range,'ef':ef,}))



def addEnvironment(request):
    user = request.user
    if user.username == '':
        return HttpResponseRedirect("/proposer/login/")
    now = timezone.now().strftime("%Y-%m-%d")
    if request.method == 'GET':
        ef =EnvironmentForm()
        return render_to_response('addEnvironment.html',RequestContext(request,{'ef':ef,}))
    else:
        ef = EnvironmentForm(request.POST)
        if ef.is_valid():
            name = ef.cleaned_data['name']
            # environment = Environment.objects.create(name=name)
            environment = Environment()
            environment.name = name
            environment.save()

            log = Log()
            log.name = "<strong>add_Environment:</strong>"
            log.description = "<strong>name:%s</strong>" % name
            log.operator = user.username
            log.operate_time = now
            log.save()

            if len(Profile.objects.filter(user=user)) ==0:
                profile = Profile()
                profile.user = user
                profile.save()
                if user.is_superuser:
                    for en in Environment.objects.all():
                        profile.environments.add(en)
            else:
                profile = Profile.objects.get(user=user)


            profile.environments.add(environment)

            for u in User.objects.all():
                if u.is_superuser:
                    pro = Profile.objects.get(user=u)
                    for envir in Environment.objects.all():
                        pro.environments.add(envir)

            return HttpResponseRedirect('/proposer/showEnvironment/')
        else:
            return render_to_response('addEnvironment.html',RequestContext(request,{'ef':ef,}))  


def modifyEnvironment(request,id):
    user = request.user
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    now = timezone.now().strftime("%Y-%m-%d")
    envir = Environment.objects.get(id=id)
    if request.method == 'GET':
        ef =EnvironmentForm(initial={'name':envir.name,})
        return render_to_response('modifyEnvironment.html',RequestContext(request,{'ef':ef,}))
    else:
        ef = EnvironmentForm(request.POST)
        if ef.is_valid():
            name = ef.cleaned_data['name']
            log = Log()
            log.name = "<strong>modify_Environment:</strong>"
            log.description="<strong>name: %s to %s</strong>" %(envir.name,name)
            log.operator = user.username
            log.operate_time = now
            log.save()

            envir.name = name
            envir.save()


            for u in User.objects.all():
                if u.is_superuser:
                    pro = Profile.objects.get(user=u)
                    for environ in Environment.objects.all():
                        pro.environments.add(environ)
            return HttpResponseRedirect('/proposer/showEnvironment/')
        else:
            return render_to_response('modifyEnvironment.html',RequestContext(request,{'ef':ef,}))


def deleteEnvironment(request,id):
    user = request.user
    if user.username == '': 
        return HttpResponseRedirect("/proposer/login/")
    now = timezone.now().strftime("%Y-%m-%d")
    print id
    envir = Environment.objects.get(id=id)
    
    log = Log()
    log.name = "<strong>delete_Environment:</strong>"
    log.description = "<strong>name:%s</strong>" % envir.name
    log.operator = user.username
    log.operate_time = now
    log.save()
   
    envir.delete()
    return HttpResponseRedirect('/proposer/showEnvironment/')
 #Environment模块  

#ServiceConfig模块
class ServiceConfigForm(ModelForm):
    config_name = forms.CharField(  
        required=True,  
        label= u"配置名称",  
        error_messages={'required': u'请输入配置名称'},  
        widget=forms.TextInput(  
            attrs={  
                'placeholder':u"配置名称",  
            }  
        ),  
    )      
    config_value = forms.CharField(  
        label= u"配置值", 
        required = False, 
        widget=forms.TextInput(  
            attrs={  
                'placeholder':u"配置值",  
            }  
        ),  
    )   
    class Meta:
        model = ServiceConfig
 	fields = "__all__" 
        

def showServiceConfig(request):
    user = request.user
    scf = ServiceConfigForm()
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    serconAll = ServiceConfig.objects.all().order_by('service') 
    objects, page_range = my_pagination(request, serconAll)
    sf = SearchForm()
    if request.method == 'GET':      
        return render_to_response('showServiceConfig.html',RequestContext(request,{'objects':objects,'page_range':page_range,'sf':sf,'scf':scf,}))
    else:
        sf = SearchForm(request.POST)
        if sf.is_valid():
            objects = ServiceConfig.objects.filter(service__service_name__contains=sf.cleaned_data['search_text']).order_by('service') 
            return render_to_response('showServiceConfig.html',RequestContext(request,{'objects':objects,'sf':sf,'scf':scf,}))
        else:
            objects, page_range = my_pagination(request, serconAll)
            return render_to_response('showServiceConfig.html',RequestContext(request,{'objects':objects,'page_range':page_range,'sf':sf,'scf':scf,}))


def addServiceConfig(request):
    user = request.user
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    now = timezone.now().strftime("%Y-%m-%d")
    if request.method == 'GET':
        scf =ServiceConfigForm()
        return render_to_response('addServiceConfig.html',RequestContext(request,{'scf':scf,}))
    else:
        scf = ServiceConfigForm(request.POST)
        if scf.is_valid():
            config_name = scf.cleaned_data['config_name']
            config_value = scf.cleaned_data['config_value']
            environment = scf.cleaned_data['environment']
            service = scf.cleaned_data['service']
            ServiceConfig.objects.create(config_name=config_name,config_value=config_value,service=service,environment=environment)

            log = Log()
            log.name = "<strong>add_ServiceConfig</strong>"
            log.description="<strong>config_name:%s  <br>config_value:%s <br> environment:%s</strong>" % (config_name,config_value,environment)
            log.operator = user.username
            log.operate_time = now
            log.save()

            return HttpResponseRedirect('/proposer/showServiceConfig/')
        else:
            return render_to_response('addServiceConfig.html',RequestContext(request,{'scf':scf,}))


def deleteServiceConfig(request,id):
    user = request.user
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    now = timezone.now().strftime("%Y-%m-%d")
    sercon = ServiceConfig.objects.get(id=id)

    log = Log()
    log.name = "<strong>delete_ServiceConfig</strong>"
    log.description = "<strong>config_name:%s  <br>config_value:%s <br>environment:%s</strong>" % (sercon.config_name,sercon.config_value,sercon.environment)
    log.operator = user.username
    log.operate_time = now
    log.save()

    sercon.delete()
    return HttpResponseRedirect('/proposer/showServiceConfig/')


def modifyServiceConfig(request,id):
    user = request.user
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    now = timezone.now().strftime("%Y-%m-%d")
    sercon = ServiceConfig.objects.get(id=id)
    if request.method == 'GET':
        scf =ServiceConfigForm(initial={'config_name':sercon.config_name,'config_value':sercon.config_value,'service':sercon.service,'environment':sercon.environment,})
        return render_to_response('modifyServiceConfig.html',RequestContext(request,{'scf':scf,}))
    else:
        scf = ServiceConfigForm(request.POST)
        if scf.is_valid():
            config_name = scf.cleaned_data['config_name']
            config_value = scf.cleaned_data['config_value']
            service = scf.cleaned_data['service']
            environment = scf.cleaned_data['environment']

            log = Log()
            log.name = "<strong>modify_ServiceConfig</strong>:"
            log.description = "<strong>config_name: %s to %s<br>  config_value: %s to %s <br> environment: %s to %s<strong>" %(sercon.config_name,config_name,sercon.config_value,config_value,sercon.environment,environment)
            log.operator = user.username
            log.operate_time = now
            log.save()

            sercon.config_name = config_name
            sercon.config_value = config_value
            sercon.environment = environment
            sercon.service = service
            sercon.save()
            return HttpResponseRedirect('/proposer/showServiceConfig/')
        else:
            return render_to_response('modifyServiceConfig.html',RequestContext(request,{'scf':scf,}))  
#ServiceConfig模块


#Hosts模块
class HostsForm(ModelForm):
    ip = forms.GenericIPAddressField(  
        required=True,  
        label= u"ip",  
        error_messages={'required': u'请输入ip'}, # bug if ip 123456789 no validate  
        widget=forms.TextInput(  
            attrs={  
                'placeholder':u"ip",  
            }  
        ),  
    )
    hostname = forms.CharField(  
        required=True,  
        label= u"主机名",  
        error_messages={'required': u'请输入主机名'},  
        widget=forms.TextInput(  
            attrs={  
                'placeholder':u"主机名",  
            }  
        ),  
    )
    chinese_name = forms.CharField(  
        required=True,  
        label= u"中文名",  
        error_messages={'required': u'请输入中文名'},  
        widget=forms.TextInput(  
            attrs={  
                'placeholder':u"中文名",  
            }  
        ),  
    )
    ansible_ssh_user = forms.CharField(  
        required=True,  
        label= u"ssh用户名",  
        error_messages={'required': u'请输入ssh用户名'},  
        widget=forms.TextInput(  
            attrs={  
                'placeholder':u"ssh用户名",  
            }  
        ),  
    )
    ansible_ssh_private_key_file = forms.FileField(
	required=False,  
        label= u"ssh密钥文件路径", 
        error_messages={'required': u'请输入ssh密钥文件路径'},  
        widget=forms.FileInput(  
            attrs={  
                'placeholder':u"默认使用密钥文件登录",  
            }  
        ),  
    )
    ansible_ssh_pass = forms.CharField(
        required = False,
        label = u"密码",
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u'默认使用密钥文件登录，密码可为空',
            }
        )
    )

    class Meta:
        model = Hosts
	fields = "__all__" 
       

def showHosts(request):
    user = request.user
    hf = HostsForm(initial={'ansible_ssh_user':'root',})
    if user.username == '':
        form = LoginForm()  
        return HttpResponseRedirect("/proposer/login/")
    hostAll = Hosts.objects.all()
    objects, page_range = my_pagination(request, hostAll)
    
    isf = IPSearchForm()
    if request.method == 'GET':  
        return render_to_response('showHosts.html',RequestContext(request,{'objects':objects,'page_range':page_range,'isf':isf,'hf':hf,}))
    else:
        isf = IPSearchForm(request.POST)
        if isf.is_valid():
            objects = Hosts.objects.filter(ip__contains=isf.cleaned_data['search_text'])
            return render_to_response('showHosts.html',RequestContext(request,{'objects':objects,'isf':isf,'hf':hf,}))
        else:
            return render_to_response('showHosts.html',RequestContext(request,{'objects':objects,'page_range':page_range,'isf':isf,'hf':hf,}))


def addHosts(request):
    user = request.user
    now = timezone.now().strftime("%Y-%m-%d")
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    if request.method == 'GET':
        hf =HostsForm(initial={'ansible_ssh_user':'root',})
        return render_to_response('addHosts.html',RequestContext(request,{'hf':hf,}))
    else:
        hf = HostsForm(request.POST,request.FILES)
        if hf.is_valid():
            ip = hf.cleaned_data['ip']
            hostname = hf.cleaned_data['hostname']
            chinese_name = hf.cleaned_data['chinese_name']
            ansible_ssh_user = hf.cleaned_data['ansible_ssh_user']
            ansible_ssh_private_key_file = hf.cleaned_data['ansible_ssh_private_key_file']
            print ansible_ssh_private_key_file
            if ansible_ssh_private_key_file != None:
                if "." in ansible_ssh_private_key_file.name:
                    return render_to_response('addHosts.html',RequestContext(request,{'hf':hf,'error':'密钥文件格式不正确'}))
                ansible_ssh_private_key_file.name = ansible_ssh_private_key_file.name +'-'+ ip
            ansible_ssh_pass = hf.cleaned_data['ansible_ssh_pass']
            print ansible_ssh_private_key_file,ansible_ssh_pass
            if ansible_ssh_private_key_file == None  and ansible_ssh_pass == "":
                hf = HostsForm(initial={'ip':ip,'hostname':hostname,'chinese_name':chinese_name,'ansible_ssh_user':ansible_ssh_user,})
                return render_to_response('addHosts.html',RequestContext(request,{'hf':hf,'error':'密钥文件和密码至少填写一个'}))
            
            environment = hf.cleaned_data['environment']
            services = hf.cleaned_data['services']
            host = Hosts.objects.create(ip=ip,hostname=hostname,chinese_name=chinese_name,ansible_ssh_user=ansible_ssh_user,ansible_ssh_private_key_file=ansible_ssh_private_key_file,ansible_ssh_pass=ansible_ssh_pass,environment=environment)
            host.save()
            for i in range(len(services)):
                host.services.add(services[i])
            host.save()

            log = Log()
            log.name = "<strong>add_Hosts</strong>"
            log.description = "<strong>ip:%s  <br>hostname:%s <br>chinese_name:%s <br>ansible_ssh_user:%s  <br>ansible_ssh_private_key_file:%s environment:%s</strong>" %(ip,hostname,chinese_name,ansible_ssh_user,ansible_ssh_private_key_file,environment)
            log.operator = user.username
            log.operate_time = now
            log.save()

            return HttpResponseRedirect('/proposer/showHosts/')
        else:
            return render_to_response('addHosts.html',RequestContext(request,{'hf':hf,}))


def deleteHosts(request,id):
    user = request.user
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    now = timezone.now().strftime("%Y-%m-%d")
    host = Hosts.objects.get(id=id)
    os.system("rm  "+MEDIA_ROOT+host.ansible_ssh_private_key_file.name)#ssh/cloud_isa

    log = Log()
    log.name = "<strong>delete_Hosts</strong>"
    log.description = "<strong>ip:%s  <br>hostname:%s  <br>chinese_name:%s <br>ansible_ssh_user:%s  <br>ansible_ssh_private_key_file:%s <br> environment:%s</strong>" % (host.ip,host.hostname,host.chinese_name,host.ansible_ssh_user,host.ansible_ssh_private_key_file,host.environment)
    log.operator = user.username
    log.operate_time = now
    log.save()

    host.delete()
    return HttpResponseRedirect('/proposer/showHosts/')


def modifyHosts(request,id):
    user = request.user
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    now = timezone.now().strftime("%Y-%m-%d")
    host = Hosts.objects.get(id=id)
    if request.method == 'GET':
        hf = HostsForm(initial = {'ip':host.ip,'hostname':host.hostname,'chinese_name':host.chinese_name,'ansible_ssh_user':host.ansible_ssh_user,'ansible_ssh_private_key_file':host.ansible_ssh_private_key_file,'ansible_ssh_pass':host.ansible_ssh_pass,'environment':host.environment,'services':host.services.all()})
        return render_to_response('modifyHosts.html',RequestContext(request,{'hf':hf,}))
    else:
        hf = HostsForm(request.POST,request.FILES)
        if hf.is_valid():
            os.system('rm  '+MEDIA_ROOT+host.ansible_ssh_private_key_file.name)
            ip = hf.cleaned_data['ip']
            hostname = hf.cleaned_data['hostname']
            chinese_name = hf.cleaned_data['chinese_name']
            ansible_ssh_user = hf.cleaned_data['ansible_ssh_user']
            ansible_ssh_private_key_file = hf.cleaned_data['ansible_ssh_private_key_file']
            if ansible_ssh_private_key_file != None:
                if "." in ansible_ssh_private_key_file.name:
                    return render_to_response('modifyHosts.html',RequestContext(request,{'hf':hf,'error':'密钥文件格式不正确'}))
                ansible_ssh_private_key_file.name = ansible_ssh_private_key_file.name +'-'+ ip
            ansible_ssh_pass = hf.cleaned_data['ansible_ssh_pass']

            print ansible_ssh_private_key_file,ansible_ssh_pass
            if ansible_ssh_private_key_file == None  and ansible_ssh_pass == "":
                hf = HostsForm(initial={'ip':ip,'hostname':hostname,'chinese_name':chinese_name,'ansible_ssh_user':ansible_ssh_user,})
                return render_to_response('modifyHosts.html',RequestContext(request,{'hf':hf,'error':'密钥文件和密码至少填写一个'}))

            environment = hf.cleaned_data['environment']
            services = hf.cleaned_data['services']

            log = Log()
            log.name = "<strong>modify_Hosts</strong>"
            log.description = "<strong>ip: %s to %s <br> hostname: %s to %s  <br> chinese_name: %s to %s <br>ansible_ssh_user: %s to %s  <br>ansible_ssh_private_key_file: %s to %s  <br>services: %s to %s<br> environment:%s to %s</strong>" %(host.ip,ip,host.hostname,hostname,host.chinese_name,chinese_name,host.ansible_ssh_user,ansible_ssh_user,host.ansible_ssh_private_key_file,ansible_ssh_private_key_file,[service for service in host.services.all()],[service for service in services.all()],host.environment,environment)
            log.operator = user.username
            log.operate_time = now
            log.save()

            host.ip = ip
            host.hostname = hostname
            host.chinese_name = chinese_name
            host.ansible_ssh_user = ansible_ssh_user
            host.ansible_ssh_private_key_file = ansible_ssh_private_key_file
            host.ansible_ssh_pass = ansible_ssh_pass
            host.environment = environment
            host.save()
            host.services.clear()
            for i in range(len(services)):
                host.services.add(services[i])
            return HttpResponseRedirect('/proposer/showHosts/')
        else:
            return render_to_response('modifyHosts.html',RequestContext(request,{'hf':hf,}))
#Hosts模块

#Playbook模块
class PlayBooksForm(ModelForm):
    usages = forms.CharField(  
        required=True,  
        label= u"用途:",  
        error_messages={'required': u'请输入用途'},  
        widget=forms.TextInput(  
            attrs={  
                'placeholder':u"用途",  
            }  
        ),  
    )      
    playbook_file = forms.FileField(
        required=True,  
        label= u"剧本文件:", 
        error_messages={'required': u'请输入剧本文件'},  
        widget=forms.FileInput(  
            attrs={  
                'placeholder':u"剧本文件",  
            }  
        ),  
    )
    class Meta:
        model = PlayBooks
	fields = "__all__" 





def checkConfig(request,playbook):
    path = (exeShellLine('pwd').strip()+'/').encode('utf-8')
    print MEDIA_ROOT+playbook.playbook_file.name
    fobj = open(MEDIA_ROOT+playbook.playbook_file.name,'r')
    configs = []
    for line in fobj.readlines():
        if "{{" and "}}" in line:
            result = re.findall(r'{{\w+}}',line)
            for config in result:
                config = config[2:][:-2]
                if config not in configs and config != 'item':
                    configs.append(config)
    fobj.close()

    obj = open(MEDIA_ROOT+"playbooks/config.yaml","r")
    content = obj.read()
    configed = []
    for config in configs:
        if config in content:
            configed.append(config)
    result =[]
    if configs != configed:
        for config in configs:
            if config not in configed and config != 'svn_version':
                result.append(config)
        return result
    obj.close()   
    return result


def showPlayBooks(request):
    pbf = PlayBooksForm()
    user = request.user
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    playbookAll = PlayBooks.objects.all()
    
    objects, page_range = my_pagination(request, playbookAll)
    unconfiged = []
    if len(PlayBooks.objects.all()) != 0:
        makeConfigFile(request,'')
        for playbook in playbookAll:
            unconfiged += checkConfig(request,playbook)

    if request.method == 'GET': 
        sf = SearchForm()
        return render_to_response('showPlayBooks.html',RequestContext(request,{'objects':objects,'page_range':page_range,'sf':sf,'unconfiged':unconfiged,'pbf':pbf,}))
    else:
        sf = SearchForm(request.POST)
        if sf.is_valid():
            objects = PlayBooks.objects.filter(service__service_name__contains=sf.cleaned_data['search_text'])
            return render_to_response('showPlayBooks.html',RequestContext(request,{'objects':objects,'sf':sf,'unconfiged':unconfiged,'pbf':pbf,}))
        else:
            sf = SearchForm()
            return render_to_response('showPlayBooks.html',RequestContext(request,{'objects':objects,'page_range':page_range,'sf':sf,'unconfiged':unconfiged,'pbf':pbf,}))


def addPlayBooks(request):
    user = request.user
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    now = timezone.now().strftime("%Y-%m-%d")
    if request.method == 'GET':
        pbf =PlayBooksForm()
        return render_to_response('addPlayBooks.html',RequestContext(request,{'pbf':pbf,}))
    else:
        pbf = PlayBooksForm(request.POST,request.FILES)
        if pbf.is_valid():
            usages = pbf.cleaned_data['usages']
            playbook_file = pbf.cleaned_data['playbook_file']
            if not playbook_file.name.endswith('.yaml'):
                error = u"剧本文件格式不正确"
                return render_to_response('addPlayBooks.html',RequestContext(request,{'pbf':pbf,'error':error,}))
            else:
                service = pbf.cleaned_data['service']
                playbook_file.name = timezone.now().strftime("%Y-%m-%d %H:%M:%S")+'-'+playbook_file.name
                PlayBooks.objects.create(usages=usages,playbook_file=playbook_file,service=service)
                log = Log()
                log.name = "<strong>add_PlayBooks<strong>"
                log.description="<strong>usages:%s  <br>playbook_file:%s<strong/>" %(usages,playbook_file)
                log.operator = user.username
                log.operate_time = now
                log.save()
            
            
                return HttpResponseRedirect("/proposer/showPlayBooks/")
        else:
            return render_to_response('addPlayBooks.html',RequestContext(request,{'pbf':pbf,}))


def deletePlayBooks(request,id):
    user = request.user
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    now = timezone.now().strftime("%Y-%m-%d")

    playbook = PlayBooks.objects.get(id=id)
    os.system("rm "+MEDIA_ROOT+playbook.playbook_file.name)
    playbook.delete()

    log = Log()
    log.name = "<strong>delete_PlayBooks</strong>"
    log.description = "<strong>usages:%s <br>playbook_file:%s</strong>" %(playbook.usages,playbook.playbook_file)
    log.operator = user.username
    log.operate_time = now
    log.save()
    return HttpResponseRedirect('/proposer/showPlayBooks/')


def modifyPlayBooks(request,id):
    user = request.user
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    now = timezone.now().strftime("%Y-%m-%d")
    playbook = PlayBooks.objects.get(id=id)
    if request.method == 'GET':
        pbf =PlayBooksForm(initial={'usages':playbook.usages,'playbook_file':playbook.playbook_file,'service':playbook.service})
        return render_to_response('modifyPlayBooks.html',RequestContext(request,{'pbf':pbf,}))
    else:
        pbf = PlayBooksForm(request.POST,request.FILES)
        if pbf.is_valid():
            os.system('rm '+MEDIA_ROOT+playbook.playbook_file.name)
            usages = pbf.cleaned_data['usages']
            playbook_file = pbf.cleaned_data['playbook_file']
            playbook_file.name = timezone.now().strftime("%Y-%m-%d %H:%M:%S")+'-'+playbook_file.name
            service = pbf.cleaned_data['service']
            log = Log()
            log.name = "<strong>modify_Playbooks:</strong>"
            log.description = "<strong>usages: %s to %s  <br>playbook_file: %s to %s</strong>"  %(playbook.usages,usages,playbook.playbook_file,playbook_file)
            log.operator = user.username
            log.operate_time = now
            log.save()

            playbook.usages = usages
            playbook.playbook_file = playbook_file
            playbook.service = service
            playbook.save()
            return HttpResponseRedirect('/proposer/showPlayBooks/')
        else:
            return render_to_response('modifyPlayBooks.html',RequestContext(request,{'pbf':pbf,})) 
#Playbook模块

#Task模块
class TaskForm(ModelForm):
    name = forms.CharField(
        required=True,  
        label= u"任务名:",  
        error_messages={'required': u'请输入任务名'},  
        widget=forms.TextInput(  
            attrs={  
                'placeholder':u"任务名",  
            }  
        ),  
    )      
    class Meta:
        model = Task
        fields = "__all__" 

def getTag(playbook):
    tags = []
    path = MEDIA_ROOT
    fobj = open(MEDIA_ROOT+playbook.playbook_file.name,'r')
    for line in fobj.readlines():
        if '- name:' in line:
            tag = line.split(':')[1].strip()
            tags.append(tag)

    return tags

def changeEnvironment(request,envir_id):
    print 'change environment '
    environment = Environment.objects.get(id=envir_id)
    hosts = Hosts.objects.filter(environment=environment)
    result = ''
    for host in hosts:
        result += "<option value=\""+str(host.id)+"\">"+str(host.ip)+"</option>"
    return HttpResponse(result)
    #str object has no attribute get method 

def tasks(request,id):
    tasks = getTag(Task.objects.get(id=id).playbook)
    result = ''
    for task in tasks:
        result += u"<input type='checkbox' checked='checked' name=\""+task+"\">"+task+"<br>"
    result += u"<input type='checkbox'  name=use_password >使用密码登录？<br>"
    return HttpResponse(result)
       
def showTask(request):
    user = request.user
    path = MEDIA_ROOT
    tf = TaskForm()
    if user.username == '':
        form = LoginForm()  
        return HttpResponseRedirect("/proposer/login/")

    taskAll = Task.objects.all()
    objects, page_range = my_pagination(request, taskAll)
    cf = ConfigForm(initial={'svn_version':'HEAD',})
    if request.method == 'GET':
        return render_to_response('showTask.html',RequestContext(request,{'objects':objects,'page_range':page_range,'cf':cf,'tf':tf,}))
    else:
        ids = []
        tags = []
        for key in request.POST:
            if request.POST[key] == 'on':
                if key.isdigit() :
                    ids.append(key)
                elif key  != 'use_password':
                    tags.append(key)
                else:
                    pass
        print tags
        use_password = False

        if request.POST.get('use_password') == 'on':
            use_password = True
        
        print use_password
        if not ids:
            id = request.POST.get('id','')
            if id == '':
                result = '<mark>没有选中就执行。。。。。</mark>'
                return render_to_response('showTask.html',RequestContext(request,{'objects':objects,'page_range':page_range,'cf':cf,'tf':tf,}))
            task = Task.objects.get(id=id)
            playbook = task.playbook.playbook_file
            fobj = file(path+task.playbook.playbook_file.name,'r')
            obj = file(path+task.playbook.playbook_file.name[:-5]+'_test'+'.yaml','w')
            for line in fobj:
                for tag in tags:
                    if tag in line:
                        line  += '          tags: '+tag+'\n'
                obj.write(line)   
            obj.close()

            cf = ConfigForm(request.POST)
            if cf.is_valid():
                delc_desc = request.POST.get('delc_desc','')
                svn_version = cf.cleaned_data['svn_version']
                hosts = cf.cleaned_data['hosts']
                print hosts
                environment = cf.cleaned_data['environment']
                  
                result = executeTask(request,id,svn_version,hosts,delc_desc,tags,environment,use_password)
                return render_to_response('showTask.html',RequestContext(request,{'objects':objects,'page_range':page_range,'cf':cf,'result':result,'tf':tf,}))
            else:
                return render_to_response('showTask.html',RequestContext(request,{'objects':objects,'page_range':page_range,'cf':cf,'tf':tf,}))
        else:
            result =''
            for id in ids:
                hosts = Task.objects.get(id=id).hosts.all()
                svn_version = 'HEAD'
                result += executeTask(request,id,svn_version,hosts,'','',Task.objects.get(id=id).environment)
            return render_to_response('showTask.html',RequestContext(request,{'objects':objects,'page_range':page_range,'cf':cf,'result':result,'tf':tf,}))
            

def addTask(request):
    user = request.user
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    now = timezone.now().strftime("%Y-%m-%d")
    if request.method == 'GET':
        tf =TaskForm()
        return render_to_response('addTask.html',RequestContext(request,{'tf':tf,}))
    else:
        tf = TaskForm(request.POST)
        if tf.is_valid():
            name = tf.cleaned_data['name']
            playbook = tf.cleaned_data['playbook']
            hosts = tf.cleaned_data['hosts']
            environment = tf.cleaned_data['environment']
           
            task = Task(name=name,playbook=playbook,environment=environment)
            task.save()
            for i in range(len(hosts)):
                task.hosts.add(hosts[i]) 
         
            log = Log()
            log.name = "<strong>add_Task:</strong>"
            log.description = "<strong>name:%s playbook:%s <br> hosts:%s <br> environment:%s</strong>" %(name,playbook,[host.ip for host in hosts],environment)
            log.operator = user.username
            log.operate_time = now
            log.save()
            return HttpResponseRedirect('/proposer/showTask/')
        else:
            return render_to_response('addTask.html',RequestContext(request,{'tf':tf,}))


def deleteTask(request,id):
    user = request.user
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    now = timezone.now().strftime("%Y-%m-%d")
    task = Task.objects.get(id=id)

    log = Log()
    log.name = "<strong>delete_Task:</strong>"
    log.description = "<strong>name:%s  <br>playbook:%s  <br>hosts:%s  <br>environment:%s</strong>" %(task.name,task.playbook,[host.ip for host in task.hosts.all()],task.environment)
    log.operator = user.username
    log.operate_time = now
    log.save()

    task.delete()
    return HttpResponseRedirect('/proposer/showTask/')


def modifyTask(request,id):
    user = request.user
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    now = timezone.now().strftime("%Y-%m-%d")
    task = Task.objects.get(id=id)
    if request.method == 'GET':
        tf =TaskForm(initial={'name':task.name,'playbook':task.playbook,'environment':task.environment,})
        return render_to_response('modifyTask.html',RequestContext(request,{'tf':tf,}))
    else:
        tf = TaskForm(request.POST)
        if tf.is_valid():
            name = tf.cleaned_data['name']
            hosts = tf.cleaned_data['hosts']
            playbook = tf.cleaned_data['playbook']
            environment = tf.cleaned_data['environment']

            log = Log()
            log.name = "<strong>modify_Task:</strong>"
            log.description = "<strong>name: %s to %s  <br>hosts: %s to %s  <br>playbook: %s to %s <br> environment:%s to %s<br></strong>" %(task.name,name,[host.ip for host in task.hosts.all()],[host.ip for host in hosts.all()],task.playbook,playbook,task.environment,environment)
            log.operator = user.username
            log.operate_time = now
            log.save()

            task.name = name
            task.playbook = playbook
            task.environment = environment
            task.save()
            task.hosts.clear()
            for i in range(len(hosts)):
                task.hosts.add(hosts[i])
            return HttpResponseRedirect('/proposer/showTask/')
        else:
            return render_to_response('modifyTask.html',RequestContext(request,{'tf':tf,})) 

#Task模块

#Log模块

def showLog(request):
    user = request.user
    if user.username == '':
        form = LoginForm()  
        
        return HttpResponseRedirect("/proposer/login/")
    logAll = Log.objects.all().order_by('-operate_time')
    objects, page_range = my_pagination(request, logAll)
    osf = operateSearchForm()
    if request.method == 'GET':   
        return render_to_response('showLog.html',RequestContext(request,{'objects':objects,'osf':osf,'page_range':page_range}))
    else:
        osf = operateSearchForm(request.POST)
        if osf.is_valid():
            objects = Log.objects.filter(name__contains=osf.cleaned_data['search_text']) 
            return render_to_response('showLog.html',RequestContext(request,{'objects':objects,'osf':osf,}))
        else:
            return render_to_response('showLog.html',RequestContext(request,{'objects':objects,'page_range':page_range,'osf':osf,}))



#生成hosts文件
def makeHostsFile(request,hosts,environment,use_password):
    path = MEDIA_ROOT

    obj = file(MEDIA_ROOT+'playbooks/ansible.cfg','w')
    ss = "[defaults]\nhostfile=./hosts"
    obj.write(ss)
    obj.close()

    hostsobj = file(MEDIA_ROOT+'playbooks/hosts','w')
    s = ''
    if not hosts:
        hosts = Hosts.objects.all()
    host_nomatch = []
    for host in hosts:
        if host.environment == environment:
            ip = host.ip
       	    hostname = host.hostname
            ansible_ssh_user = host.ansible_ssh_user
            ansible_ssh_private_key_file = host.ansible_ssh_private_key_file.name
            ansible_ssh_pass = host.ansible_ssh_pass
            if not use_password :

    	        s += '['+hostname+']'+'\n'+ip+'    ansible_ssh_user='+ansible_ssh_user+'   ansible_ssh_private_key_file='+path+ansible_ssh_private_key_file+'\n'  
            else:
                s += '['+hostname+']'+'\n'+ip+'    ansible_ssh_user='+ansible_ssh_user+'   ansible_ssh_pass='+ansible_ssh_pass+'\n'  
                

        else:
            host_nomatch.append(host.ip)

    hostsobj.write(s)
    hostsobj.close()
    return host_nomatch

        
#生成config.yaml文件   


def makeConfigFile(request,environment):
    if not environment:
        serconAll = ServiceConfig.objects.all().order_by('service','config_value')
    else:
        serconAll = ServiceConfig.objects.filter(environment=environment).order_by('service','config_value')

    print MEDIA_ROOT+'playbooks/config.yaml'       
    configobj = file(MEDIA_ROOT+'playbooks/config.yaml','w')
    s ='---\n\n'
    for i in range(len(serconAll)):
        config_name = serconAll[i].config_name
        config_value = serconAll[i].config_value
        if config_name in s:
            break#如果config_name相同，但是所属的环境不同
        if i >=1:
            if serconAll[i].service == serconAll[i-1].service:
                s += config_name+": "+config_value+'\n'
            else:
                s += '\n#'+serconAll[i].service.service_name+" config\n"+config_name+': '+config_value+'\n'
        else:
            s += '#'+serconAll[i].service.service_name+" config\n"+config_name+': '+config_value+'\n'
    configobj.write(s)
    configobj.close()

import os
def exeShellLine(cmd):
    r = os.popen(cmd)
    text = r.read()
    r.close()
    return text

import re

def executeTask(request,id,svn_version,hosts,delc_desc,tags,environment,use_password):
    user = request.user

    if len(Profile.objects.filter(user=user)) == 0:
        profile = Profile.objects.create(user=user)
        
        for environment in Environment.objects.all():
            profile.environments.add(environment)
        profile.save()

    pro = Profile.objects.get(user=user)

    path = MEDIA_ROOT
    # /home/liuyang11/upload/
    # /home/liuyang11/git/ansible-web/service/
    print path
    if user.username == '':
        return HttpResponseRedirect("/proposer/login/")
        
    if environment in pro.environments.all() or user.is_superuser:
        now = timezone.now().strftime("%Y-%m-%d")
        sercon = ServiceConfig.objects.filter(config_name='svn_version')
        if sercon:
            sercon[0].config_value = svn_version
            sercon[0].environment = environment
            sercon[0].save()
        else:
            glob = Service.objects.filter(service_name='global')
            if glob:
                pass
            else:
                Service.objects.create(service_name="global")
            ServiceConfig.objects.create(config_name='svn_version',config_value=svn_version,service=Service.objects.get(service_name='global'),environment=environment)
        task = Task.objects.get(id=id)


        host_nomatch = makeHostsFile(request,hosts,environment,use_password)
        makeConfigFile(request,environment)
        #遍历
        fobj = open(path+task.playbook.playbook_file.name,'r')
        configs = []
        for line in fobj.readlines():
            if "{{" and "}}" in line:
                result = re.findall(r'{{\w+}}',line)
                for config in result:
                    config = config[2:][:-2]
                    if config not in configs and config != 'item':
                        configs.append(config)
        fobj.close()

        obj = open(path+"playbooks/config.yaml","r")
        content = obj.read()
        configed = []
        for config in configs:
            if config in content:
                configed.append(config)

        if configs != configed:
            result = '<mark style="color:red;">'+task.environment.name+u'环境下,需要的所有配置:<br>'
            for config in configs:
                result += config+','
            result += '<br>'
            result +=u'已经完成的配置:<br>'
            for config in configed:
                result += config+','
            result += '</mark>'
            return result
        obj.close()       
        #将svn_version改回HEAD  
        sercon = ServiceConfig.objects.get(config_name='svn_version')
        sercon.config_value = 'HEAD'
        sercon.save()
     
        exeShellLine('chmod  -x  '+path+'playbooks/*')
        exeShellLine('chmod 600 '+path+'ssh/*')
        
        if len(tags) != 0:
            cmd = "ansible-playbook -i "+path+"playbooks/hosts  "+path+"playbooks/*_test.yaml"+' --tags=\"'
            for i in range(len(tags)):
                if i == (len(tags)-1):
                    cmd += tags[i]+'\"'
                else:
                    cmd += tags[i] +','
            print cmd
            r = os.popen(cmd)
        else:
            r = os.popen("ansible-playbook -i "+path+"playbooks/hosts  "+path+task.playbook.playbook_file.name)
            
        execute_result = ''
        if len(host_nomatch) != 0:
            print host_nomatch
            result = "<mark>"+str([ip for ip in host_nomatch])+u"发布环境不匹配"
        else:
            result = ''
        result += '<div style="background:black;color:white;width:100%;height:100%;">'
        for line in r.readlines():
            execute_result += line + '<br>'
            if "ok:" in line:
                result += '<span style="color:#006633;">%s</span><br>' % line
            elif "changed:" in line:
                result += '<span style="color:#ff9900;">%s</span><br>' % line
            elif 'skipping:' in line:
                result += '<span style="color:#00ffcc;">%s</span><br>' % line
            else:
                result += "<span>%s</span><br>" % line
        result += '</div>'
        log = Log()
        log.name = "<strong>executeTask</strong>"
        str_hosts = ''
        for host in hosts:
            str_hosts += host.ip +','
        log.description = "<strong>hosts<strong/>:%s  <br> <strong>playbook<strong/>:%s <br> <strong>execute_result:<strong/>%s  <br> <strong>description:<strong/>%s" % (str_hosts,task.playbook,execute_result,delc_desc)
        log.operator = user.username
        log.operate_time = now
        log.save()
        if len(tags) != 0:
            exeShellLine('rm  '+path+'playbooks/*_test.yaml')
        return result
    else:
        result = u"<mark>权限不够，请联系管理员获取权限</mark>"
        return result

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user',]
                
def showPower(request):
    user = request.user
    now = timezone.now().strftime("%Y-%m-%d")
    profileAll = Profile.objects.all()
    objects,page_range = my_pagination(request,profileAll)
    pf = ProfileForm()
    if not user.is_superuser:
        return HttpResponseRedirect('/proposer/index')
    else:
        if request.method == 'GET':
            return render_to_response('showPower.html',RequestContext(request,{'objects':objects,'page_range':page_range,'pf':pf,}))
        else:
            pf = ProfileForm(request.POST)
            if pf.is_valid():
                id = request.POST['id']
                profile = Profile.objects.get(id=id)
                environments = pf.cleaned_data['environments']
                
                log = Log()
                log.name = "<strong>modify_Power:</strong>"

                log.description=u"<strong>environments: %s to %s</strong>" %([environment.name for environment in profile.environments.all()],[environment.name for environment in environments.all()])
                log.operator = user.username
                log.operate_time = now
                log.save()

                profile.environments.clear()
                for environment in environments:
                    profile.environments.add(environment)
                profile.save()
                return HttpResponseRedirect('/proposer/showPower/')
            else:
                return render_to_response('showPower.html',RequestContext(request,{'objects':objects,'page_range':page_range,'pf':pf,}))




