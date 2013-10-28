from django.forms import Form, ChoiceField, IntegerField, CharField
from django.forms.util import ErrorList

from stocksite.models import Company

class TradeForm(Form):
  action = ChoiceField(choices=(
                                ('buy', 'BUY'),
                                ('sell', 'SELL'),
                               ))
  amount = IntegerField(min_value = 1)
  company = CharField(max_length = 10)
  
  def performAction(self, user):
    if self.is_valid():
      profile = user.get_profile()
      compName = self.cleaned_data['company']
      amount = self.cleaned_data['amount']
      
      if self.cleaned_data['action'] == 'buy':
        success, error = profile.buy_stock(compName, amount)
      else: # self.cleaned_data['action'] == 'sell'
        success, error = profile.sell_stock(compName, amount)
      
      if not(success):
        self._errors["perfAction"] = ErrorList([error])
      
      return success
    else:
      return False