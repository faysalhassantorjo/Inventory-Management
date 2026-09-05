from django import forms
from .models import FabricPurchase

class FabricPurchaseForm(forms.ModelForm):
    class Meta:
        model = FabricPurchase
        fields = [
            'supplier', 'fabric_name', 'color', 'quantity', 
            'unit', 'unit_price', 'total_price', 'purchase_date', 
            'reference_number', 'notes'
        ]
        widgets = {
            'supplier': forms.Select(
                attrs={
                    'class': (
                        'block w-full rounded-md border border-gray-300 '
                        'px-3 py-2 text-sm text-gray-900 bg-white '
                        'focus:border-gray-500 focus:ring-1 focus:ring-gray-500'
                    )
                }
            ),
            'fabric_name': forms.TextInput(
                attrs={
                    'class': (
                        'block w-full rounded-md border border-gray-300 '
                        'px-3 py-2 text-sm text-gray-900 '
                        'placeholder-gray-400 '
                        'focus:border-gray-500 focus:ring-1 focus:ring-gray-500'
                    ),
                    'placeholder': 'Fabric Name'
                }
            ),
            'color': forms.TextInput(
                attrs={
                    'class': (
                        'block w-full rounded-md border border-gray-300 '
                        'px-3 py-2 text-sm text-gray-900 '
                        'placeholder-gray-400 '
                        'focus:border-gray-500 focus:ring-1 focus:ring-gray-500'
                    ),
                    'placeholder': 'Color'
                }
            ),
            'quantity': forms.NumberInput(
                attrs={
                    'class': (
                        'block w-full rounded-md border border-gray-300 '
                        'px-3 py-2 text-sm text-gray-900 '
                        'focus:border-gray-500 focus:ring-1 focus:ring-gray-500'
                    ),
                    'min': 0,
                    'step': '0.01'
                }
            ),
            'unit': forms.TextInput(
                attrs={
                    'class': (
                        'block w-full rounded-md border border-gray-300 '
                        'px-3 py-2 text-sm text-gray-900 '
                        'placeholder-gray-400 '
                        'focus:border-gray-500 focus:ring-1 focus:ring-gray-500'
                    ),
                    'placeholder': 'e.g. meters, yards'
                }
            ),
            'unit_price': forms.NumberInput(
                attrs={
                    'class': (
                        'block w-full rounded-md border border-gray-300 '
                        'px-3 py-2 text-sm text-gray-900 '
                        'focus:border-gray-500 focus:ring-1 focus:ring-gray-500'
                    ),
                    'min': 0,
                    'step': '0.01'
                }
            ),
            'total_price': forms.NumberInput(
                attrs={
                    'class': (
                        'block w-full rounded-md border border-gray-300 '
                        'px-3 py-2 text-sm text-gray-900 '
                        'focus:border-gray-500 focus:ring-1 focus:ring-gray-500'
                    ),
                    'min': 0,
                    'step': '0.01'
                }
            ),
            'purchase_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': (
                        'block w-full rounded-md border border-gray-300 '
                        'px-3 py-2 text-sm text-gray-900 '
                        'focus:border-gray-500 focus:ring-1 focus:ring-gray-500'
                    )
                }
            ),
            'reference_number': forms.TextInput(
                attrs={
                    'class': (
                        'block w-full rounded-md border border-gray-300 '
                        'px-3 py-2 text-sm text-gray-900 '
                        'placeholder-gray-400 '
                        'focus:border-gray-500 focus:ring-1 focus:ring-gray-500'
                    ),
                    'placeholder': 'Invoice or Ref No'
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
        }
