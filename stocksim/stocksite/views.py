# Standard library imports
import datetime

# Third party imports
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

# Local imports
from stocksite.models import Company

@login_required
def home(request):
    return render(request, 'home.html')
    return render(request, 'login.html', {})
    
def companies(request):
    return render(request, 'companies.html', {'companies': [], 'yesterday': None, 'today': None})
    
def company(request, name):
    try:
      company = Company.objects.get(shortName=name)
    except Company.DoesNotExist:
      # TODO: give pretty error
      return HttpResponseNotFound('<h1>Company does not exist</h1>')
    
    return render(request, 'company.html', {'company':company})
    
def settings(request):
    return render(request, 'settings.html', {})

