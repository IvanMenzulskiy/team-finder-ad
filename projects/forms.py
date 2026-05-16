from django import forms

from .constants import DESCRIPTION_TEXTAREA_ROWS
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на Github",
            "status": "Статус",
        }
        widgets = {
            "description": forms.Textarea(
                attrs={"rows": DESCRIPTION_TEXTAREA_ROWS},
            ),
            "status": forms.Select(choices=Project.Status.choices),
        }
