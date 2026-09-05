from django import forms
from .models import Supplier

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'phone', 'email', 'address', 'notes', 'is_active']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': (
                        'block w-full rounded-md border border-gray-300 '
                        'px-3 py-2 text-sm text-gray-900 '
                        'placeholder-gray-400 '
                        'focus:border-gray-500 focus:ring-1 focus:ring-gray-500'
                    ),
                    'placeholder': 'Supplier Name'
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'class': (
                        'block w-full rounded-md border border-gray-300 '
                        'px-3 py-2 text-sm text-gray-900 '
                        'placeholder-gray-400 '
                        'focus:border-gray-500 focus:ring-1 focus:ring-gray-500'
                    ),
                    'placeholder': 'Phone Number'
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': (
                        'block w-full rounded-md border border-gray-300 '
                        'px-3 py-2 text-sm text-gray-900 '
                        'placeholder-gray-400 '
                        'focus:border-gray-500 focus:ring-1 focus:ring-gray-500'
                    ),
                    'placeholder': 'Email Address'
                }
            ),
            'address': forms.Textarea(
                attrs={
                    'class': (
                        'block w-full rounded-md border border-gray-300 '
                        'px-3 py-2 text-sm text-gray-900 '
                        'placeholder-gray-400 '
                        'focus:border-gray-500 focus:ring-1 focus:ring-gray-500'
                    ),
                    'rows': 3,
                    'placeholder': 'Supplier Address'
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': (
                        'block w-full rounded-md border border-gray-300 '
                        'px-3 py-2 text-sm text-gray-900 '
                        'placeholder-gray-400 '
                        'focus:border-gray-500 focus:ring-1 focus:ring-gray-500'
                    ),
                    'rows': 3,
                    'placeholder': 'Additional Notes'
                }
            ),
            'is_active': forms.CheckboxInput(
                attrs={
                    'class': (
                        'w-4 h-4 rounded border-gray-300 '
                        'text-gray-900 focus:ring-gray-500'
                    )
                }
            ),
        }
