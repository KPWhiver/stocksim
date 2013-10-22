import os, sys

apache_configuration = os.path.dirname(__file__)
project = os.path.dirname(apache_configuration)
workspace = os.path.dirname(project)
sys.path.append(workspace)
sys.path.append('/home/ubuntu/stocksim/stocksim/stocksite')
sys.path.append('/home/ubuntu/stocksim/stocksim')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stocksite.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
