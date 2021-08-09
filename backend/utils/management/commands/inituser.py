from django.core.management.base import BaseCommand

from account.models import AdminType, ProblemPermission, User, UserProfile
from utils.shortcuts import rand_str  # NOQA


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--username", type=str)
        parser.add_argument("--action", type=str)

    def handle(self, *args, **options):
        username = options["username"]
        action = options["action"]

        if not(username and action):
            self.stdout.write(self.style.ERROR("Invalid args"))
            exit(1)

        if action == "create_super_admin":
            if User.objects.filter(id=1).exists():
                self.stdout.write(self.style.SUCCESS(f"User {username} exists, operation ignored"))
                exit()

            user = User.objects.create(username=username, admin_type=AdminType.SUPER_ADMIN,
                                       problem_permission=ProblemPermission.ALL)
            user.save()
            UserProfile.objects.create(user=user)

            self.stdout.write(self.style.SUCCESS("User created"))
        else:
            raise ValueError("Invalid action")
