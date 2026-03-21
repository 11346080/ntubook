from django import forms
from .models import Listing


class ListingCreateForm(forms.ModelForm):
    """建立刊登的表單（W4 最小骨架用）"""

    class Meta:
        model = Listing
        fields = [
            'book',
            'used_price',
            'condition_level',
            'origin_academic_year',
            'origin_term',
            'origin_class_group',
            'description',
        ]
