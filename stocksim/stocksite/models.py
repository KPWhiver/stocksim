from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db import models
from djangotoolbox.fields import EmbeddedModelField, ListField

from django_mongodb_engine.contrib import MongoDBManager

import datetime

from bson.son import SON

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    money = models.DecimalField(max_digits=50, decimal_places=4, default=100000)
    stocks = ListField(EmbeddedModelField('OwnedStock'))
    
    def get_stock(self, name):
      return next((stock for stock in self.stocks if stock.company.shortName == name), None)
      
    def get_or_create_stock(self, name):
      stock = self.get_stock(name)
      if stock is None:
        comp = Company.objects.get(shortName=name)
        stock = OwnedStock(company=comp, amount=0)
        self.stocks.append(stock)
        self.save()
        
      return stock
    
    def buy_stock(self, name, amount):
      comp = Company.objects.get(shortName=name)
      price = comp.dailyData[-1].askPrice * amount
      if price > self.money:
        return False
      
      self.money -= price
      stock = self.get_or_create_stock(name)
      stock.amount += amount
      
      self.save()
      stock.save()
      return True
    
    def sell_stock(self, name, amount):
      stock = self.get_or_create_stock(name)
      if stock.amount < amount:
        return False
      
      comp = Company.objects.get(shortName=name)
      price = comp.dailyData[-1].bidPrice * amount
      
      self.money += price
      stock.amount -= amount
      
      self.save()
      stock.save()
      return True
      
    
    objects = MongoDBManager()

class Company(models.Model):
    shortName = models.CharField(max_length=50) # Please insert appropriate max_length
    longName = models.CharField(max_length=50) # Please insert appropriate max_length
    historicData = ListField(EmbeddedModelField('History'))
    dailyData = ListField(EmbeddedModelField('TimePoint'))
    
    objects = MongoDBManager()

    def percentageChange(self):
      """ Returns the percentage change relative to yesterdays closing price"""
      try:
        curPrice = self.dailyData[-1].currentPrice
        closePrice = self.historicData[-1].closePrice
      except IndexError: # Just return zero when no historic or dailyData is available yet
        return 0.0
      return (curPrice - closePrice)/closePrice * 100

class History(models.Model):
    date = models.DateField(default=datetime.date.today)
    #date = models.DateField(auto_now_add=True)
    volume = models.BigIntegerField()
    adjustedClosePrice = models.DecimalField(max_digits=10, decimal_places=2)
    highPrice = models.DecimalField(max_digits=10, decimal_places=2)
    lowPrice = models.DecimalField(max_digits=10, decimal_places=2)
    closePrice = models.DecimalField(max_digits=10, decimal_places=2)
    openPrice = models.DecimalField(max_digits=10, decimal_places=2)
    
class TimePoint(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    currentPrice = models.DecimalField(max_digits=10, decimal_places=2)
    bidPrice = models.DecimalField(max_digits=10, decimal_places=2)
    askPrice = models.DecimalField(max_digits=10, decimal_places=2)
    
class OwnedStock(models.Model):
    company = models.ForeignKey(Company)
    amount = models.BigIntegerField()
    
    def get_value(self):
        return self.amount * self.company.dailyData[-1].currentPrice

# Result from map reduces in totalWorth()
class CompanyOwners(models.Model):
    value = EmbeddedModelField('Owners')
    
    objects = MongoDBManager()
    
class Owners(models.Model):
    owners = ListField(EmbeddedModelField('Owner'))
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
class Owner(models.Model):
    amount = models.BigIntegerField()
    userid = models.ForeignKey(UserProfile)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a matching profile whenever a user object is created."""
    if created: 
        profile, new = UserProfile.objects.get_or_create(user=instance)

# Map/Reduce methods

# Result of totalStockBought()
# Result can be found back by something like:
#     comp = Company.objects.get(shortName="GOOG")
#     amount = StockCount.objects.get(company=comp).amount
class StockCount(models.Model):
    company = models.ForeignKey(Company)
    amount = models.BigIntegerField()

def totalWorth():
    mapfuncUser = """
    function() 
    {
        var id = this._id;
        this.stocks.forEach(function(stock) 
        {
          var perUser = {amount: stock.amount, userid: id}; 
          emit(stock.company_id, {owners: [perUser], price: 0});
        }
        )
    }
    """    
    mapfuncCompany = """
    function() 
    { 
        var data = this.historicData[this.historicData.length - 1];
        if(data !== undefined)
        {
          emit(this._id, {owners: [], price: data.closePrice});
        }
        else
        {
          emit(this._id, {owners: [], price: 0});
        }       
    }
    """    
    reducefunc = """
    function reduce(key, values) 
    {
        var result = {owners: [], price: 0};
        
        values.forEach(function(value) 
        {
            if(value.owners !== [])
            {
              result.owners = result.owners.concat(value.owners); 
            }
            
            if(result.price === 0 && value.price !== 0)
            {
              result.price = value.price;
            }
        });
        
        return result;
    }
    """
    res = Company.objects.map_reduce(mapfuncCompany, reducefunc, out={'reduce': 'stocksite_companyowners'})
    res = UserProfile.objects.map_reduce(mapfuncUser, reducefunc, out={'reduce': 'stocksite_companyowners'})
    
    for pair in res:
        print pair
    
    mapfunc = """
    function()
    {
      var price = this.value.price;
      this.value.owners.forEach(function(owner)
      {
        emit(owner.userid, owner.amount * price);
      });    
    }
    """
    
    reducefunc = """
    function(key, values)
    {
      return Array.sum(values);
    }
    """
    
    res = CompanyOwners.objects.map_reduce(mapfunc, reducefunc, 'temp_worth', drop_collection=True)
    
    for item in CompanyOwners.objects.all():
        item.delete()
    
    for pair in res:
        print pair
        
        
    
        """
        comp = Company.objects.get(id=pair.key)
        count = None

        if StockCount.objects.filter(company = comp).exists():
            count = StockCount.objects.get(company = comp)
            count.amount = pair.value
        else:
            count = StockCount(company=comp, amount=pair.value)

        count.save()
        """

def totalStockBought():
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
    res = UserProfile.objects.map_reduce(mapfunc, reducefunc, 'temp_stockcount', drop_collection=True)

    for pair in res:
        comp = Company.objects.get(id=pair.key)
        count = None

        if StockCount.objects.filter(company = comp).exists():
            count = StockCount.objects.get(company = comp)
            count.amount = pair.value
        else:
            count = StockCount(company=comp, amount=pair.value)

        count.save()

