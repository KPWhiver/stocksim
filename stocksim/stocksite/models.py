from django.db import models
from djangotoolbox.fields import EmbeddedModelField

class Company(models.Model):
    shortName = models.CharField()
    longName = models.CharField()
    historicData = ListField(EmbeddedModelField('History'))
    dailyData = ListField(EmbeddedModelField('TimePoint'))

class History(models.Model):
    date = models.DateField(auto_now_add=True)
    volume = models.BigIntegerField()
    adjustedClosePrice = models.DecimalField(..., max_digits=10, decimal_places=2)
    highPrice = models.DecimalField(..., max_digits=10, decimal_places=2)
    lowPrice = models.DecimalField(..., max_digits=10, decimal_places=2)
    closePrice = models.DecimalField(..., max_digits=10, decimal_places=2)
    openPrice = models.DecimalField(..., max_digits=10, decimal_places=2)
    
class TimePoint(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    currentPrice = models.DecimalField(..., max_digits=10, decimal_places=2)
    bidPrice = models.DecimalField(..., max_digits=10, decimal_places=2)
    askPrice = models.DecimalField(..., max_digits=10, decimal_places=2)

#class User:
