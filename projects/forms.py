from django import forms

from projects.constants import DESCRIPTION_TEXTAREA_ROWS
from projects.models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        widgets = {
            "description": forms.Textarea(
                attrs={"rows": DESCRIPTION_TEXTAREA_ROWS},
            ),
            "status": forms.Select(choices=Project.Status.choices),
        }
