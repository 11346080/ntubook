from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    """首次登入建立 UserProfile 的表單"""

    class Meta:
        model = UserProfile
        fields = [
            'display_name',
            'student_no',
            'program_type',
            'department',
            'class_group',
            'grade_no',
        ]
