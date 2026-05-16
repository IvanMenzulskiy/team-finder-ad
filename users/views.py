"""Вьюхи приложения users."""
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .constants import USERS_PAGE_SIZE
from .forms import LoginForm, PasswordForm, ProfileForm, RegisterForm
from .models import Skill, User


def register_view(request):
    if request.user.is_authenticated:
        return redirect("projects:list")
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("users:login")
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("projects:list")
    form = LoginForm(request.POST or None, request=request)
    if form.is_valid():
        login(request, form.user)
        return redirect("projects:list")
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def participants_view(request):
    queryset = (
        User.objects.all()
        .prefetch_related("skills")
        .order_by("-date_joined")
    )

    chosen_skill = (request.GET.get("skill") or "").strip()
    if chosen_skill:
        queryset = queryset.filter(skills__name__iexact=chosen_skill).distinct()

    page = Paginator(queryset, USERS_PAGE_SIZE).get_page(
        request.GET.get("page"),
    )
    return render(
        request,
        "users/participants.html",
        {
            "participants": page.object_list,
            "page_obj": page,
            "active_skill": chosen_skill,
            "all_skills": Skill.objects.all(),
        },
    )


def profile_view(request, pk):
    target = get_object_or_404(
        User.objects.prefetch_related("skills"), pk=pk,
    )
    return render(request, "users/user-details.html", {"user": target})


@login_required
def edit_profile_view(request):
    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )
    if form.is_valid():
        form.save()
        return redirect("users:detail", request.user.id)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password_view(request):
    form = PasswordForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("users:detail", request.user.id)
    return render(request, "users/change_password.html", {"form": form})
