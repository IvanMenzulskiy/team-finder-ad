"""Команда ``manage.py seed_data`` — заполняет БД из JSON."""
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from projects.models import Project
from users.models import Skill, User

DEFAULT_DATA_FILE = Path(__file__).parent / "data" / "seed.json"


class Command(BaseCommand):
    help = "Заполнить БД демо-пользователями, навыками и проектами из JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=Path,
            default=DEFAULT_DATA_FILE,
            help="JSON-файл с данными",
        )

    def handle(self, *args, **opts):
        source: Path = opts["file"]
        if not source.exists():
            raise CommandError(f"Не найден файл: {source}")

        payload = json.loads(source.read_text(encoding="utf-8"))

        self._seed_skills(payload.get("skills", ()))
        self._seed_users(payload.get("users", ()))
        self._seed_projects(payload.get("projects", ()))
        if payload.get("superuser"):
            self._seed_admin(payload["superuser"])

        self.stdout.write(self.style.SUCCESS("Готово."))

    def _seed_skills(self, names):
        for name in names:
            skill, fresh = Skill.objects.get_or_create(name=name)
            if fresh:
                self._ok(f"Навык «{skill.name}»")

    def _seed_users(self, records):
        for r in records:
            user, fresh = User.objects.get_or_create(
                email=r["email"],
                defaults={
                    "name": r["name"],
                    "surname": r["surname"],
                    "phone": r.get("phone") or None,
                    "about": r.get("about", ""),
                    "github_url": r.get("github_url", ""),
                },
            )
            if fresh:
                user.set_password(r["password"])
                user.save()
                self._ok(f"Пользователь {user.email}")
            else:
                self.stdout.write(f"Уже есть: {user.email}")

            skill_names = r.get("skills") or []
            if skill_names:
                user.skills.set(
                    Skill.objects.filter(name__in=skill_names),
                )

    def _seed_projects(self, records):
        for r in records:
            owner = User.objects.get(email=r["owner_email"])
            project, fresh = Project.objects.get_or_create(
                name=r["name"],
                owner=owner,
                defaults={
                    "description": r.get("description", ""),
                    "status": r.get("status", Project.Status.OPEN),
                    "github_url": r.get("github_url", ""),
                },
            )
            project.participants.add(owner)
            if fresh:
                self._ok(f"Проект «{project.name}»")
            else:
                self.stdout.write(f"Уже есть: «{project.name}»")

    def _seed_admin(self, record):
        if User.objects.filter(is_superuser=True).exists():
            return
        User.objects.create_superuser(
            email=record["email"],
            password=record["password"],
            name=record["name"],
            surname=record["surname"],
        )
        self._ok(f"Суперюзер {record['email']} / {record['password']}")

    def _ok(self, line):
        self.stdout.write(self.style.SUCCESS(line))
