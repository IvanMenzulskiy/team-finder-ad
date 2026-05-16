"""Вьюхи приложения projects.

Сюда же вынесены AJAX-эндпоинты для управления навыками пользователей —
их URL ожидаются ``static/js/skills.js`` под префиксом ``/projects/``.
"""
import json
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from projects.constants import PROJECTS_PAGE_SIZE
from projects.forms import ProjectForm
from projects.models import Project
from projects.service import get_project_or_json_404, get_user_or_json
from users.constants import SKILL_AUTOCOMPLETE_LIMIT
from users.models import Skill


def _project_qs():
    return Project.objects.select_related("owner").prefetch_related(
        "participants",
    )


def _paginate(request, queryset):
    return Paginator(queryset, PROJECTS_PAGE_SIZE).get_page(
        request.GET.get("page"),
    )


def project_list_view(request):
    queryset = _project_qs().order_by("-created_at")
    page = _paginate(request, queryset)
    return render(
        request,
        "projects/project_list.html",
        {"projects": page.object_list, "page_obj": page},
    )


def project_detail_view(request, pk):
    project = get_object_or_404(_project_qs(), pk=pk)
    return render(
        request,
        "projects/project-details.html",
        {"project": project},
    )


@login_required
def create_project_view(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.owner = request.user
        obj.save()
        obj.participants.add(request.user)
        return redirect("projects:detail", obj.pk)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False},
    )


@login_required
def edit_project_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id and not request.user.is_staff:
        return redirect("projects:detail", project.pk)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects:detail", project.pk)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True},
    )


@login_required
@require_POST
def complete_project_view(request, pk):
    project, error = get_project_or_json_404(pk)
    if error is not None:
        return error
    if project.owner_id != request.user.id:
        return JsonResponse(
            {"status": "forbidden"}, status=HTTPStatus.FORBIDDEN,
        )
    if project.status != Project.Status.OPEN:
        return JsonResponse(
            {"status": "error", "project_status": project.status},
            status=HTTPStatus.BAD_REQUEST,
        )
    project.status = Project.Status.CLOSED
    project.save(update_fields=["status"])
    return JsonResponse(
        {"status": "ok", "project_status": project.status},
    )


@login_required
@require_POST
def toggle_participate_view(request, pk):
    project, error = get_project_or_json_404(pk)
    if error is not None:
        return error
    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        return JsonResponse({"status": "ok", "participant": False})
    project.participants.add(request.user)
    return JsonResponse({"status": "ok", "participant": True})


@require_GET
def skill_autocomplete_view(request):
    """Автокомплит по навыкам: ``GET /projects/skills/?q=...``."""
    query = (request.GET.get("q") or "").strip()
    if not query:
        return JsonResponse([], safe=False)

    matches = (
        Skill.objects.filter(name__icontains=query)
        .order_by("name")[:SKILL_AUTOCOMPLETE_LIMIT]
        .values("id", "name")
    )
    return JsonResponse(list(matches), safe=False)


@login_required
@require_POST
def add_skill_view(request, pk):
    """Добавить навык в профиль: ``POST /projects/<user_id>/skills/add/``.

    Тело либо ``{"skill_id": N}``, либо ``{"name": "Django"}``.
    """
    user, error = get_user_or_json(pk, request.user)
    if error is not None:
        return error

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "bad_json"}, status=HTTPStatus.BAD_REQUEST,
        )

    skill = None
    skill_id = payload.get("skill_id")
    if skill_id is not None:
        skill = Skill.objects.filter(pk=skill_id).first()
    if skill is None:
        name = (payload.get("name") or "").strip()
        if not name:
            return JsonResponse(
                {"status": "missing_name"}, status=HTTPStatus.BAD_REQUEST,
            )
        skill, _ = Skill.objects.get_or_create(name=name)

    user.skills.add(skill)
    return JsonResponse({"id": skill.id, "name": skill.name})


@login_required
@require_POST
def remove_skill_view(request, pk, skill_id):
    """Убрать навык: ``POST /projects/<user_id>/skills/<skill_id>/remove/``."""
    user, error = get_user_or_json(pk, request.user)
    if error is not None:
        return error
    skill = Skill.objects.filter(pk=skill_id).first()
    if skill is None:
        return JsonResponse(
            {"status": "not_found"}, status=HTTPStatus.NOT_FOUND,
        )
    user.skills.remove(skill)
    return JsonResponse({"status": "ok"})
