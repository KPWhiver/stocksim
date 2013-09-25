from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
import datetime

def home(request):
    return render_to_response('home.html', {}, context_instance=RequestContext(request))
    return render_to_response('login.html', {}, context_instance=RequestContext(request))
    
def companies(request):
    return render_to_response('companies.html', {}, context_instance=RequestContext(request))
    return render_to_response('company.html', {}, context_instance=RequestContext(request))
    
def settings(request):
    return render_to_response('settings.html', {}, context_instance=RequestContext(request))

    
