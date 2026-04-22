from django import forms
from .models import Task, Project
from django.contrib.auth import get_user_model

User = get_user_model()

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'project', 'assignee', 'status', 'priority', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Название задачи'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Описание задачи'}),
            'project': forms.Select(attrs={'class': 'form-input'}),
            'assignee': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'priority': forms.Select(attrs={'class': 'form-input'}),
            'deadline': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'participants']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Название проекта'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Описание проекта'}),
            'participants': forms.SelectMultiple(attrs={'class': 'form-input', 'size': '5'}),
        }