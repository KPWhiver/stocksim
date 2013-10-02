# Standard library imports
import datetime

# Third party imports
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

import feedparser

# Local imports
from stocksite.models import Company, History, TimePoint, UserProfile

@login_required
def home(request):   
    d = feedparser.parse('http://finance.yahoo.com/news/?format=rss')
    numOfItems = min(10, len(d.entries))
    
    news = []
    
    for entry in d.entries[0:numOfItems]:
      dateParsed = entry.published_parsed
      date = datetime.datetime(dateParsed.tm_year, dateParsed.tm_mon, dateParsed.tm_mday, dateParsed.tm_hour, dateParsed.tm_min)
    
      news += [entry.title, entry.link, date]
    """
    news = [['Klaas crowned world emperor', '#', datetime.date(2013, 10, 1)], 
            ['Resistance to Klaasolution slowly ceases', '#', datetime.date(2013, 9, 29)], 
            ['Klaasolution has started, millions march the streets to overthrow governments', '#', datetime.date(2013, 9, 26)], 
            ['Klaas proclaims himself world leader, calls on overthrowing governments', '#', datetime.date(2013, 9, 22)], 
            ['Normal day, no news', '#', datetime.date(2013, 9, 13)]]    
    """
    return render(request, 'home.html', {'news': news})
    
def companies(request):
    if Company.objects.count() == 0:
        Company(shortName = 'GOOG',
                longName = 'Google',
                historicData = [History(volume = 10000, adjustedClosePrice = 800, highPrice = 810, lowPrice = 790, closePrice = 801, openPrice = 803)],
                dailyData = [TimePoint(currentPrice = 799, bidPrice = 799.5, askPrice = 799.5)]).save()
        Company(shortName = 'APPL',
                longName = 'Apple',
                historicData = [History(volume = 9000, adjustedClosePrice = 80, highPrice = 81, lowPrice = 79, closePrice = 81, openPrice = 83)],
                dailyData = [TimePoint(currentPrice = 79, bidPrice = 79.5, askPrice = 78.5)]).save()
    
    companies = Company.objects.all()

    searchText = request.GET.get('search')
    
    return render(request, 'companies.html', {'companies': companies, 'searchText': searchText})
    
def company(request, name):
    try:
      company = Company.objects.get(shortName=name)
    except Company.DoesNotExist:
      # TODO: give pretty error
      return HttpResponseNotFound('<h1>Company does not exist</h1>')
    
    return render(request, 'company.html', {'company':company})
    
def settings(request):
    return render(request, 'settings.html', {})
    
def mapReduce():
    mapfunc = """
    function() 
    {
      this.stocks.forEach(
        function(stock) { emit(stock.company_id, stock.amount) }
      )
    }
    """
    
    reducefunc = """
    function reduce(key, values) 
    {
      return Array.sum(values)
    }
    """

    for pair in UserProfile.objects.map_reduce(mapfunc, reducefunc, 'stockcount'):
        print pair.key, pair.value


