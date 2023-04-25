from optparse import make_option

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from django_q.cluster import Cluster
from django_q.brokers import get_broker



class Command(BaseCommand):
    # Translators: help text for qcluster management command
    help = _("Starts Wishbook 2 Clusters.")
    option_list = BaseCommand.option_list + (
        make_option('--run-once',
                    action='store_true',
                    dest='run_once',
                    default=False,
                    help='Run once and then stop.'),
    )

    def handle(self, *args, **options):
        clusters_names = ['priority', 'trivenilabs']
        for c in clusters_names:
            q = Cluster(get_broker(c))
            q.start()
            if options.get('run_once', False):
                q.stop()
