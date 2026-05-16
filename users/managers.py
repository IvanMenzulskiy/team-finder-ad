from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """Менеджер кастомного пользователя (вход по email)."""

    use_in_migrations = True

    def _create(self, email, password, **extra):
        if not email:
            raise ValueError("Email обязателен")
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create(email, password, **extra)

    def create_superuser(self, email=None, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        if not extra.get("is_staff"):
            raise ValueError("Superuser требует is_staff=True")
        if not extra.get("is_superuser"):
            raise ValueError("Superuser требует is_superuser=True")
        return self._create(email, password, **extra)
