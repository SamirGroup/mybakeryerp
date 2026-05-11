from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = 'Create default admin superuser and role groups'

    def handle(self, *args, **kwargs):
        for name in ['admin', 'accountant', 'hr', 'seller']:
            Group.objects.get_or_create(name=name)
        self.stdout.write('Groups created.')

        if not User.objects.filter(username='admin').exists():
            u = User.objects.create_superuser(username='admin', password='admin123', email='')
            group, _ = Group.objects.get_or_create(name='admin')
            u.groups.add(group)
            self.stdout.write(self.style.SUCCESS("Superuser 'admin' created (password: admin123). Change it immediately!"))
        else:
            self.stdout.write("User 'admin' already exists.")
