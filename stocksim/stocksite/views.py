# Standard library imports
from datetime import datetime, date
import json
import time


# Third party imports
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

import feedparser

# Local imports
from stocksite.models import Company, History, TimePoint, UserProfile
from stocksite.decorators import ajax_required
from stocksite.forms import TradeForm

def register(request):
    if request.method == 'POST':
        if not request.user.is_authenticated():
            form = UserCreationForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')

                user = User.objects.create(username=username)
                if password:
                    user.set_password(password)
                else:
                    user.set_unusable_password()

                user.save()

                new_user = authenticate(username=username, password=password)
                login(request, new_user)
                
                return HttpResponseRedirect("/")

    return HttpResponseRedirect("/")

@login_required
def home(request):   
    d = feedparser.parse('http://finance.yahoo.com/news/?format=rss')
    numOfItems = min(10, len(d.entries))
    
    news = []
    
    for entry in d.entries[0:numOfItems]:
        dateParsed = entry.published_parsed
        date = datetime(dateParsed.tm_year, dateParsed.tm_mon, dateParsed.tm_mday, dateParsed.tm_hour, dateParsed.tm_min)
        
        news.append([entry.title, entry.link, date])

    return render(request, 'home.html', {'news': news})

@login_required
def companies(request):
    if Company.objects.count() == 0:
        Company(shortName = 'GOOG',
                longName = 'Google',
                historicData = [History(volume = 10000, adjustedClosePrice = 800, highPrice = 810, lowPrice = 790, closePrice = 801, openPrice = 803)],
                dailyData = [TimePoint(currentPrice = 799, bidPrice = 799.5, askPrice = 799.5)]).save()
        Company(shortName = 'AAPL',
                longName = 'Apple',
                historicData = [History(volume = 9000, adjustedClosePrice = 80, highPrice = 81, lowPrice = 79, closePrice = 81, openPrice = 83)],
                dailyData = [TimePoint(currentPrice = 79, bidPrice = 79.5, askPrice = 78.5)]).save()
    
    companies = Company.objects.all()

    searchText = request.GET.get('search')
    
    return render(request, 'companies.html', {'companies': companies, 'searchText': searchText})

@login_required
def company(request, name):
    try:
      company = Company.objects.get(shortName=name)
    except Company.DoesNotExist:
      # TODO: give pretty error
      return HttpResponseNotFound('<h1>Company does not exist</h1>')
    stocks = request.user.get_profile().get_stock(name)
    
    # ownStock is None when the user has not yet bought stock of that company
    if not stocks is None:
      return render(request, 'company.html', {'company':company, 'amount_stocks':stocks.amount, 'value_stocks':stocks.get_value()})
    else:
      return render(request, 'company.html', {'company':company, 'amount_stocks':0, 'value_stocks':0})

def rest(request, name):
    try:
      company = Company.objects.get(shortName=name)
    except Company.DoesNotExist:
      return HttpResponse(json.dumps([]), content_type="application/json")
    
    response_data = []

    for data in company.historicData:
      timestamp = (data.date.toordinal() - date(1970, 1, 1).toordinal()) *24*60*60*1000
      response_data.append([timestamp, float(data.openPrice)])
    
    for data in company.dailyData:
      timestamp = (data.time - datetime(1970, 1, 1)).total_seconds() * 1000
      response_data.append([timestamp, float(data.currentPrice)])
    
    return HttpResponse(json.dumps(response_data), content_type="application/json")
    
@login_required
@require_POST
@ajax_required
def trade_stock(request):
    form = TradeForm(request.POST)
    if form.is_valid():
      form.performAction(request.user)
    else:
      print form.errors # Return the error so that it can be displayed
    # Return some data which can be used to refresh the page
    #response_data = {}
    #
    #response_data["errors"] = form.errors
    #test = form.errors
    #return HttpResponse(test)#, content_type="application/json")

@login_required
def settings(request):
    return render(request, 'settings.html', {})
