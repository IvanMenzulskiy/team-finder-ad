"""Тесты приложения users."""
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from .models import Skill, User
from .utils import to_canonical_phone

PASSWORD = "qwerty12345"


class UserModelTests(TestCase):
    def test_avatar_generated_on_save(self):
        u = User.objects.create_user(
            email="a@example.com", password=PASSWORD,
            name="A", surname="One",
        )
        self.assertTrue(u.avatar.name)
        self.assertTrue(u.check_password(PASSWORD))

    def test_phone_canonical_on_save(self):
        u = User.objects.create_user(
            email="b@example.com", password=PASSWORD,
            name="B", surname="Two", phone="89001234567",
        )
        self.assertEqual(u.phone, "+79001234567")

    def test_to_canonical_phone(self):
        self.assertEqual(to_canonical_phone("89001234567"), "+79001234567")
        self.assertEqual(to_canonical_phone("+79001234567"), "+79001234567")
        self.assertIsNone(to_canonical_phone(None))

    def test_superuser(self):
        admin = User.objects.create_superuser(
            email="root@example.com", password=PASSWORD,
            name="R", surname="A",
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class AuthFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.existing = User.objects.create_user(
            email="existing@example.com", password=PASSWORD,
            name="Old", surname="User",
        )

    def test_signup_redirects_to_login(self):
        r = self.client.post(reverse("users:register"), {
            "name": "New", "surname": "Guy",
            "email": "new@example.com", "password": PASSWORD,
        })
        self.assertRedirects(r, reverse("users:login"))
        self.assertTrue(
            User.objects.filter(email="new@example.com").exists(),
        )

    def test_signup_blocks_duplicate(self):
        r = self.client.post(reverse("users:register"), {
            "name": "Dup", "surname": "Mail",
            "email": "existing@example.com", "password": PASSWORD,
        })
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertContains(r, "уже существует")

    def test_login_and_logout(self):
        r = self.client.post(reverse("users:login"), {
            "email": "existing@example.com", "password": PASSWORD,
        })
        self.assertEqual(r.status_code, HTTPStatus.FOUND)
        r = self.client.get(reverse("users:logout"))
        self.assertEqual(r.status_code, HTTPStatus.FOUND)

    def test_login_wrong_password(self):
        r = self.client.post(reverse("users:login"), {
            "email": "existing@example.com", "password": "incorrect",
        })
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertContains(r, "Неверный")


class SkillFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.django_skill = Skill.objects.create(name="Django")
        cls.react_skill = Skill.objects.create(name="React")

        cls.user_with_django = User.objects.create_user(
            email="django_dev@example.com", password=PASSWORD,
            name="DjangoExpert", surname="Backend",
        )
        cls.user_with_django.skills.add(cls.django_skill)

        cls.user_with_react = User.objects.create_user(
            email="react_dev@example.com", password=PASSWORD,
            name="ReactExpert", surname="Frontend",
        )
        cls.user_with_react.skills.add(cls.react_skill)

    def test_no_filter_shows_everyone(self):
        r = self.client.get(reverse("users:list"))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertContains(r, "DjangoExpert")
        self.assertContains(r, "ReactExpert")

    def test_filter_by_django_keeps_only_django_users(self):
        r = self.client.get(reverse("users:list") + "?skill=Django")
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertContains(r, "DjangoExpert")
        self.assertNotContains(r, "ReactExpert")

    def test_filter_unknown_skill_returns_empty(self):
        r = self.client.get(reverse("users:list") + "?skill=Cobol")
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertNotContains(r, "DjangoExpert")
        self.assertNotContains(r, "ReactExpert")
