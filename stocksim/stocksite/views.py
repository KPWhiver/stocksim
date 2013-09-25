from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
import datetime

def home(request):
    return render(request, 'home.html')
    return render(request, 'login.html', {})
    
def companies(request):
    return render(request, 'companies.html', {})
    
def company(request, name):
    return render(request, 'company.html', {})
    
def settings(request):
    return render(request, 'settings.html', {})

    
