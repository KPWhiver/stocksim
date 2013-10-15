import datetime
import time
import csv

try:
    # py3
    from urllib.request import Request, urlopen, HTTPError
    from urllib.parse import urlencode
except ImportError:
    # py2
    from urllib2 import Request, urlopen, HTTPError
    from urllib import urlencode
    
from stocksite.models import Company, History, TimePoint

def requestFinanceData(symbols, stat):
    url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=%s' % (symbols, stat)
    req = Request(url)
    resp = urlopen(req)
    return str(resp.read().decode('utf-8').strip())

def getHistoricalPrices(symbol, startDate, endDate):
    """
    Get historical prices for the given ticker symbol.
    Date format is 'YYYY-MM-DD'

    Returns a nested dictionary (dict of dicts).
    outer dict keys are dates ('YYYY-MM-DD')
    """
    params = urlencode({
        's': symbol,
        'a': startDate.month - 1,
        'b': startDate.day - 1,
        'c': startDate.year,
        'd': endDate.month - 1,
        'e': endDate.day - 1,
        'f': endDate.year,
        'g': 'd',
        'ignore': '.csv',
    })
    url = 'http://ichart.yahoo.com/table.csv?%s' % params
    req = Request(url)
    resp = urlopen(req)
    content = str(resp.read().decode('utf-8').strip())
    daily_data = content.splitlines()
    hist_dict = dict()
    keys = daily_data[0].split(',')
    for day in daily_data[1:]:
        day_data = day.split(',')
        date = day_data[0]
        hist_dict[date] = \
            {keys[1]: day_data[1],
             keys[2]: day_data[2],
             keys[3]: day_data[3],
             keys[4]: day_data[4],
             keys[5]: day_data[5],
             keys[6]: day_data[6]}
    return hist_dict
    
def getTodayData(symbols):
    pass

def updateHistoricData():
    companies = Company.objects.all()

    for company in companies:
        today = datetime.datetime.today()
        data = getHistoricalPrices(company.shortName, today, today)
        data = data.values()[0]
        company.historicData.append(History(volume = data['Volume'], adjustedClosePrice = data['Adj Close'], highPrice = data['High'], lowPrice = data['Low'], closePrice = data['Close'], openPrice = data['Open']))
        company.save()
        time.sleep(5)
   
def updateDailyDataRange(companies, startIndex, length):
    companyString = ''
    
    for company in companies[startIndex:startIndex + length]:
        companyString += company.shortName + '+'

    perCompany = requestFinanceData(companyString[:-1], 'l1ba').split('\r\n')  
 
    
    for companyIndex, company in enumerate(companies[startIndex:startIndex + length]):
        values = perCompany[companyIndex].split(',')
        
        try:
            price = float(values[0])
        except ValueError, e:
            print 'Error occurred:', e, 'company:', company.shortName, 'values:', values
            continue
            
        try:
            bid = float(values[1])
        except:
            bid = 0
            
        try:
            ask = float(values[2])
        except:
            ask = 0
        
        company.dailyData.append(TimePoint(currentPrice = price, bidPrice = bid, askPrice = ask))
        company.save()
        
    print startIndex + length, 'done'
        
def updateDailyData():
    companies = Company.objects.all()
    
    for index in range(len(companies) // 100):
        updateDailyDataRange(companies, index * 100, 100)
        time.sleep(5)
        
    updateDailyDataRange(companies, (len(companies) // 100) * 100, len(companies) % 100)
        
def updateVolumes():
    pass

def addCompanies(interval = 1):
    with open('companylist.csv', 'rb') as companiescsv:
        companyReader = csv.reader(companiescsv)
        
        for index, company in enumerate(companyReader):
            if index % interval != 0:
                continue
        
            print company[0].strip()
        
            if Company.objects.filter(shortName = company[0]).exists():
                continue
                
            Company(shortName = company[0].strip(), longName = company[1].strip(), historicData = [], dailyData = []).save()

def fillDatabase():
    companies = Company.objects.all()

    for company in companies:
        company.historicData = []
        print company.shortName
        
        yesterday = datetime.datetime.today() - datetime.timedelta(1)
        monthago = yesterday - datetime.timedelta(30)
        data = {}
        try:
            data = getHistoricalPrices(company.shortName, monthago, yesterday)
        except HTTPError, e:
            print 'Error occurred:', e, 'company:', company.shortName
            continue
            
        for (date, values) in data.items():
            day = datetime.date(int(date[0:4]), int(date[5:7]), int(date[8:10]))
            company.historicData.append(History(date = date, volume = values['Volume'], adjustedClosePrice = values['Adj Close'], 
                                        highPrice = values['High'], lowPrice = values['Low'], closePrice = values['Close'], openPrice = values['Open']))
        
        company.save()
        time.sleep(5)
        

