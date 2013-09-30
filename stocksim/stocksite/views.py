# Standard library imports
import datetime

# Third party imports
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

# Local imports
from stocksite.models import Company, History, TimePoint, UserProfile

@login_required
def home(request):   
    return render(request, 'home.html')
    
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
    
    return render(request, 'companies.html', {'companies': companies})
    
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


