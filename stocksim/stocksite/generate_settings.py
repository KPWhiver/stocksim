import argparse
import os
import sys
import time

if __name__ == "__main__":
  # Read arguments
  parser = argparse.ArgumentParser(description='Generate a database settings file')
  parser.add_argument('server', nargs='?', help='address of a mongoDB instance (default: localhost)', default="")
  parser.add_argument('port', type=int, nargs='?', help='port of a mongoDB instance (default: 27017)', default=27017)
  
  args = parser.parse_args()
  
  host = args.server
  port = args.port
  
  # Create the settings file
  with open('db_settings.py', 'w') as file:
    file.write(\
"""DATABASES = {
    'default': {
        'ENGINE': 'django_mongodb_engine',
        'NAME': 'django_db', 
        'USER': '', 
        'PASSWORD': '',
        'HOST': '%s', 
        'PORT': %d, 
    }
}

""" % (host, port))
  
  time.sleep(1)
  
  # Set environment
  os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
  
  from django.contrib.sites.models import Site
  # Create a site, if needed
  sites = Site.objects.all()
  if len(sites) == 0:
    s = Site()
    s.save()
  else:
    s = sites[0]
  
  site_id = s.id
  
  # Append the site id
  with open('db_settings.py', 'a') as file:
    file.write("""SITE_ID = "%s" """ % (site_id))
