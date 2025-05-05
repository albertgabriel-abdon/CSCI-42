from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create a superuser if none exists'

    def handle(self, *args, **options):
        if not User.objects.filter(is_superuser=True).exists():
            username = 'albert'
            email = 'albert.abdon@student.ateneo.edu'
            password = 'albert'
            
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS('Superuser created with username: albert and password: albert'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser already exists'))

        if not User.objects.filter(username='dummyuser').exists():

            username = 'dummyuser'
            email = 'dummyuser@example.com'
            password = 'dummyuser'
            User.objects.create_user(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS('Dummy user created with username: dummyuser and password: dummyuser'))
        else:
            self.stdout.write(self.style.SUCCESS('Dummy user already exists'))

