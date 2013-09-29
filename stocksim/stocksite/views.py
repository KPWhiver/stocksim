import datetime

from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from stocksite.models import Company

@login_required
def home(request):
    return render(request, 'home.html')
    return render(request, 'login.html', {})
    
def companies(request):
    return render(request, 'companies.html', {})
    
def company(request, name):
    try:
      company = Company.objects.get(shortName=name)
    except Company.DoesNotExist:
      # TODO: give pretty error
      return HttpResponseNotFound('<h1>Company does not exist</h1>')
    
    return render(request, 'company.html', {'company':company})
    
def settings(request):
    return render(request, 'settings.html', {})

