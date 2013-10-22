from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
import backend

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--companies',
            action='store_true',
            dest='companies',
            default=False,
            help='Add companies to the database'),
        make_option('--fill',
            action='store_true',
            dest='fill',
            default=False,
            help='Fill the database with entries for the companies currently in the database'),
        make_option('--daily',
            action='store_true',
            dest='daily',
            default=False,
            help='Update the daily data in the database'),
        make_option('--historical',
            action='store_true',
            dest='historical',
            default=False,
            help='Update the historical data in the database'),
        make_option('--daemon',
            action='store_true',
            dest='daemon',
            default=False,
            help='Starts a process that periodically updates the database'),
        )

    def handle(self, *args, **options):
        if options['companies']:
          num = 1
          if len(args) > 0:
            try:
              num = int(args[0])
            except:
              raise CommandError('Invalid companies interval')
          
          backend.addCompanies(num)
        elif options['fill']:
          backend.fillDatabase()
        elif options['daily']:
          backend.updateDailyData()
        elif options['historical']:
          backend.updateHistoricData()
        elif options['daemon']:
          backend.startDaemon()
        else:
          raise CommandError('Missing flag')