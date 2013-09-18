from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
import datetime

def home(request):
    return render_to_response('home.html', {'string': 'hello world'}, context_instance=RequestContext(request))
