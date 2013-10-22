from datetime import datetime, date
import json

from django.http import HttpResponse

from stocksite.models import Company

def companies(request, name):
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

def user(request):
    data = []
    if request.user.is_authenticated():
      for totalWorthEntry in request.user.get_profile().totalWorthData:
        timestamp = (totalWorthEntry.time - datetime(1970, 1, 1)).total_seconds() * 1000
        data.append([timestamp, float(totalWorthEntry.value)])
    
    return HttpResponse(json.dumps(data), content_type="application/json")