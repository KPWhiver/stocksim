from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
import datetime

@login_required
def home(request):
    return render(request, 'home.html')
    return render(request, 'login.html', {})
    
def companies(request):
    return render(request, 'companies.html', {'companies': [], 'yesterday': None, 'today': None})
    
def company(request, name):
    return render(request, 'company.html', {})
    
def settings(request):
    return render(request, 'settings.html', {})

    
