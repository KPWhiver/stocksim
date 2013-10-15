from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from stocksite.models import totalWorth

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--totalWorth',
            action='store_true',
            dest='totalWorth',
            default=False,
            help='Run the totalWorth map reduce'),
        )

    def handle(self, *args, **options):
        if options['totalWorth']:
          totalWorth()
        else:
          raise CommandError('Missing flag')