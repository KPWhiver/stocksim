from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db import models
from djangotoolbox.fields import EmbeddedModelField, ListField

from django_mongodb_engine.contrib import MongoDBManager


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    money = models.DecimalField(max_digits=50, decimal_places=4, default=0)
    stocks = ListField(EmbeddedModelField('OwnedStock'))
    
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
    date = models.DateField(auto_now_add=True)
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

