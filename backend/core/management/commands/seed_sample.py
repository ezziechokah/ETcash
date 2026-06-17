from django.core.management.base import BaseCommand

from sample_servers.seed import seed_all


class Command(BaseCommand):
    help = 'Seed the database with sample company, users, and demo transactions'

    def handle(self, *args, **options):
        seed_all(verbose=True)
