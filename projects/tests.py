"""Тесты приложения projects + skill-эндпоинты."""
import json
from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from users.models import Skill, User

from .models import Project

PASSWORD = "qwerty12345"


class PublicPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            email="owner@example.com", password=PASSWORD,
            name="Author", surname="Owner",
        )
        cls.project = Project.objects.create(
            name="Sample", description="d", owner=cls.owner,
        )

    def test_anon_reads_list(self):
        r = self.client.get(reverse("projects:list"))
        self.assertEqual(r.status_code, HTTPStatus.OK)

    def test_anon_reads_detail(self):
        r = self.client.get(
            reverse("projects:detail", args=[self.project.pk]),
        )
        self.assertEqual(r.status_code, HTTPStatus.OK)

    def test_anon_cant_create(self):
        r = self.client.get(reverse("projects:create"))
        self.assertEqual(r.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("users:login"), r["Location"])


class CreateProjectTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.maker = User.objects.create_user(
            email="maker@example.com", password=PASSWORD,
            name="Maker", surname="One",
        )
        cls.maker_cli = Client()
        cls.maker_cli.force_login(cls.maker)

    def test_create_assigns_owner(self):
        r = self.maker_cli.post(reverse("projects:create"), {
            "name": "Brand new",
            "description": "x",
            "github_url": "https://github.com/maker/repo",
            "status": Project.Status.OPEN,
        })
        self.assertEqual(r.status_code, HTTPStatus.FOUND)
        proj = Project.objects.get(name="Brand new")
        self.assertEqual(proj.owner, self.maker)
        self.assertTrue(
            proj.participants.filter(pk=self.maker.pk).exists(),
        )

    def test_create_rejects_non_github(self):
        r = self.maker_cli.post(reverse("projects:create"), {
            "name": "Bad",
            "description": "x",
            "github_url": "https://gitlab.com/x",
            "status": Project.Status.OPEN,
        })
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertContains(r, "github")


class AjaxProjectTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            email="ajax_o@example.com", password=PASSWORD,
            name="O", surname="O",
        )
        cls.guest = User.objects.create_user(
            email="ajax_g@example.com", password=PASSWORD,
            name="G", surname="G",
        )
        cls.owner_cli = Client()
        cls.owner_cli.force_login(cls.owner)
        cls.guest_cli = Client()
        cls.guest_cli.force_login(cls.guest)

    def test_toggle_participate(self):
        project = Project.objects.create(name="P1", owner=self.owner)
        url = reverse("projects:toggle_participate", args=[project.pk])
        r = self.guest_cli.post(url)
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertTrue(r.json()["participant"])
        r = self.guest_cli.post(url)
        self.assertFalse(r.json()["participant"])

    def test_complete_owner_only(self):
        project = Project.objects.create(name="P2", owner=self.owner)
        url = reverse("projects:complete", args=[project.pk])
        r = self.guest_cli.post(url)
        self.assertEqual(r.status_code, HTTPStatus.FORBIDDEN)
        r = self.owner_cli.post(url)
        self.assertEqual(r.status_code, HTTPStatus.OK)
        project.refresh_from_db()
        self.assertEqual(project.status, Project.Status.CLOSED)


class SkillEndpointsTests(TestCase):
    """AJAX-эндпоинты для управления навыками профиля."""

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            email="skill_owner@example.com", password=PASSWORD,
            name="Skiller", surname="Owner",
        )
        cls.other = User.objects.create_user(
            email="other@example.com", password=PASSWORD,
            name="Other", surname="One",
        )
        cls.owner_cli = Client()
        cls.owner_cli.force_login(cls.owner)
        cls.other_cli = Client()
        cls.other_cli.force_login(cls.other)
        cls.existing_skill = Skill.objects.create(name="Existing")

    def test_autocomplete_empty_q_returns_empty(self):
        r = self.client.get(reverse("projects:skills_search"))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.json(), [])

    def test_autocomplete_finds_skill(self):
        r = self.client.get(
            reverse("projects:skills_search") + "?q=Exis",
        )
        self.assertEqual(r.status_code, HTTPStatus.OK)
        names = [s["name"] for s in r.json()]
        self.assertIn("Existing", names)

    def test_add_skill_by_id_attaches_to_user(self):
        r = self.owner_cli.post(
            reverse("projects:skill_add", args=[self.owner.pk]),
            data=json.dumps({"skill_id": self.existing_skill.pk}),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(r.json()["name"], "Existing")
        self.assertTrue(
            self.owner.skills.filter(pk=self.existing_skill.pk).exists(),
        )

    def test_add_skill_by_name_creates_new_skill(self):
        r = self.owner_cli.post(
            reverse("projects:skill_add", args=[self.owner.pk]),
            data=json.dumps({"name": "DjangoREST"}),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertTrue(
            Skill.objects.filter(name="DjangoREST").exists(),
        )
        self.assertTrue(
            self.owner.skills.filter(name="DjangoREST").exists(),
        )

    def test_other_user_cant_modify_my_skills(self):
        r = self.other_cli.post(
            reverse("projects:skill_add", args=[self.owner.pk]),
            data=json.dumps({"skill_id": self.existing_skill.pk}),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, HTTPStatus.FORBIDDEN)

    def test_remove_skill(self):
        self.owner.skills.add(self.existing_skill)
        r = self.owner_cli.post(
            reverse(
                "projects:skill_remove",
                args=[self.owner.pk, self.existing_skill.pk],
            ),
        )
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertFalse(
            self.owner.skills.filter(pk=self.existing_skill.pk).exists(),
        )
