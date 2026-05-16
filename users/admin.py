"""Админка для моделей User и Skill."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import (
    AdminPasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)
from django.db.models import Count
from django.utils.html import format_html

from .constants import ADMIN_AVATAR_THUMB_PX
from .models import Skill, User


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "users_count")
    list_display_links = ("id", "name")
    search_fields = ("name",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _users_count=Count("users"),
        )

    @admin.display(description="Пользователей", ordering="_users_count")
    def users_count(self, obj):
        return obj._users_count


class _CreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "name", "surname")


class _ChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    add_form = _CreateForm
    form = _ChangeForm
    change_password_form = AdminPasswordChangeForm
    model = User

    list_display = (
        "id",
        "avatar_tag",
        "email",
        "name",
        "surname",
        "skills_count",
        "is_staff",
        "is_active",
    )
    list_display_links = ("id", "email")
    list_filter = ("is_staff", "is_active", "skills")
    search_fields = ("email", "name", "surname")
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined", "last_login")
    filter_horizontal = ("skills",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Личные данные",
            {"fields": (
                "name", "surname", "avatar", "about", "phone", "github_url",
                "skills",
            )},
        ),
        (
            "Права",
            {"fields": (
                "is_active", "is_staff", "is_superuser",
                "groups", "user_permissions",
            )},
        ),
        ("Даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email", "name", "surname", "password1", "password2",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("skills")
            .annotate(_skills_count=Count("skills"))
        )

    @admin.display(description="Аватар")
    def avatar_tag(self, obj):
        if not obj.avatar:
            return ""
        return format_html(
            '<img src="{}" width="{}" height="{}" '
            'style="border-radius:50%;object-fit:cover" />',
            obj.avatar.url,
            ADMIN_AVATAR_THUMB_PX,
            ADMIN_AVATAR_THUMB_PX,
        )

    @admin.display(description="Навыки", ordering="_skills_count")
    def skills_count(self, obj):
        return obj._skills_count
