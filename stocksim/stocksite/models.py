from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db import models
from djangotoolbox.fields import EmbeddedModelField, ListField

from django_mongodb_engine.contrib import MongoDBManager

import datetime


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    money = models.DecimalField(max_digits=50, decimal_places=4, default=0)
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
        return UserProfile.objects.map_reduce(mapfunc, reducefunc, 'stockcount')

class Company(models.Model):
    shortName = models.CharField(max_length=50) # Please insert appropriate max_length
    longName = models.CharField(max_length=50) # Please insert appropriate max_length
    historicData = ListField(EmbeddedModelField('History'))
    dailyData = ListField(EmbeddedModelField('TimePoint'))

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
    

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a matching profile whenever a user object is created."""
    if created: 
        profile, new = UserProfile.objects.get_or_create(user=instance)



#class User:

