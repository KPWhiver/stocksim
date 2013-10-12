from django.forms import Form, ChoiceField, IntegerField, CharField

from stocksite.models import Company

class TradeForm(Form):
  action = ChoiceField(choices=(
                                ('buy', 'BUY'),
                                ('sell', 'SELL'),
                               ))
  amount = IntegerField(min_value = 0)
  company = CharField(max_length = 10)
  
  def performAction(self, user):
    if self.is_valid():
      profile = user.get_profile()
      compName = self.cleaned_data['company']
      amount = self.cleaned_data['amount']
      
      if self.cleaned_data['action'] == 'buy':
        return profile.buy_stock(compName, amount)
      else: # self.cleaned_data['action'] == 'sell'
        return profile.sell_stock(compName, amount)
      