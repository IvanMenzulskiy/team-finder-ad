"""Модель проекта."""
from django.conf import settings
from django.db import models
from django.urls import reverse

from users.utils import github_validator

from .constants import NAME_MAX_LENGTH


class Project(models.Model):

    class Status(models.TextChoices):
        OPEN = "open", "Открыт"
        CLOSED = "closed", "Закрыт"

    name = models.CharField("Название", max_length=NAME_MAX_LENGTH)
    description = models.TextField("Описание", blank=True, default="")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор",
    )
    github_url = models.URLField(
        "GitHub",
        blank=True,
        default="",
        validators=[github_validator],
    )
    status = models.CharField(
        "Статус",
        max_length=max(len(value) for value, _ in Status.choices),
        choices=Status.choices,
        default=Status.OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name="Участники",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("projects:detail", args=[self.pk])
