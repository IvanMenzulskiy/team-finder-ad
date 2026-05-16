from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("list/", views.project_list_view, name="list"),
    path("create-project/", views.create_project_view, name="create"),

    # AJAX: автокомплит навыков (общий для всех пользователей).
    path("skills/", views.skill_autocomplete_view, name="skills_search"),

    # AJAX: управление навыками профиля пользователя.
    # JS из static/js/skills.js шлёт сюда POST'ы.
    path(
        "<int:pk>/skills/add/",
        views.add_skill_view,
        name="skill_add",
    ),
    path(
        "<int:pk>/skills/<int:skill_id>/remove/",
        views.remove_skill_view,
        name="skill_remove",
    ),

    # Проектные AJAX-эндпоинты.
    path(
        "<int:pk>/complete/",
        views.complete_project_view,
        name="complete",
    ),
    path(
        "<int:pk>/toggle-participate/",
        views.toggle_participate_view,
        name="toggle_participate",
    ),

    path("<int:pk>/", views.project_detail_view, name="detail"),
    path("<int:pk>/edit/", views.edit_project_view, name="edit"),
]
