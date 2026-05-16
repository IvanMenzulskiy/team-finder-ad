from http import HTTPStatus

from django.http import JsonResponse

from projects.models import Project
from users.models import User


def get_project_or_json_404(pk):
    project = Project.objects.filter(pk=pk).first()
    if project is None:
        return None, JsonResponse(
            {"status": "not_found"}, status=HTTPStatus.NOT_FOUND,
        )
    return project, None


def get_user_or_json(pk, request_user):
    """Возвращает пользователя; пускает только хозяина профиля."""
    user = User.objects.filter(pk=pk).first()
    if user is None:
        return None, JsonResponse(
            {"status": "not_found"}, status=HTTPStatus.NOT_FOUND,
        )
    if user.pk != request_user.pk and not request_user.is_staff:
        return None, JsonResponse(
            {"status": "forbidden"}, status=HTTPStatus.FORBIDDEN,
        )
    return user, None
