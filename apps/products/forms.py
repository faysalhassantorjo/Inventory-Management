from django import forms
from .models import Category, Product, ProductSpecification, ProductImage, Discount


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "is_active"]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": (
                        "mt-1 block w-full "
                        "border border-gray-300 rounded-md "
                        "bg-white "
                        "text-sm text-gray-900 "
                        "px-3 py-2 "
                        "placeholder-gray-400 "
                        "focus:outline-none "
                        "focus:ring-1 focus:ring-gray-400 "
                        "focus:border-gray-400 "
                        "transition-colors duration-150"
                    ),
                    "placeholder": "e.g. T-Shirts",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": (
                        "mt-1 block w-full "
                        "border border-gray-300 rounded-md "
                        "bg-white "
                        "text-sm text-gray-900 "
                        "px-3 py-2 "
                        "placeholder-gray-400 "
                        "resize-y "
                        "focus:outline-none "
                        "focus:ring-1 focus:ring-gray-400 "
                        "focus:border-gray-400 "
                        "transition-colors duration-150"
                    ),
                    "placeholder": "Brief description of this category...",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": (
                        "w-4 h-4 "
                        "rounded "
                        "border-gray-300 "
                        "text-blue-600 "
                        "focus:ring-2 focus:ring-blue-500/30 "
                        "cursor-pointer"
                    ),
                }
            ),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        from django.utils.text import slugify

        if not instance.slug:
            base_slug = slugify(instance.name)
            slug = base_slug
            counter = 1

            while (
                Category.objects
                .filter(slug=slug)
                .exclude(pk=instance.pk)
                .exists()
            ):
                slug = f"{base_slug}-{counter}"
                counter += 1

            instance.slug = slug

        if commit:
            instance.save()

        return instance


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product

        fields = [
            "name",
            "category",
            "description",
            "base_price",
            "thumbnail",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": (
                        "block w-full rounded-md border border-gray-300 "
                        "px-3 py-2 text-sm text-gray-900 "
                        "placeholder-gray-400 "
                        "focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
                    ),
                    "placeholder": "e.g. Premium Cotton Kurti",
                }
            ),

            "category": forms.Select(
                attrs={
                    "class": (
                        "block w-full rounded-md border border-gray-300 "
                        "px-3 py-2 text-sm text-gray-900 "
                        "bg-white "
                        "focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
                    ),
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": (
                        "block w-full rounded-md border border-gray-300 "
                        "px-3 py-2 text-sm text-gray-900 "
                        "placeholder-gray-400 "
                        "focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
                    ),
                    "rows": 5,
                    "placeholder": "Describe the product...",
                }
            ),

            "base_price": forms.NumberInput(
                attrs={
                    "class": (
                        "block w-full rounded-md border border-gray-300 "
                        "px-3 py-2 text-sm text-gray-900 "
                        "focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
                    ),
                    "min": 0,
                    "step": 1,
                    "placeholder": "e.g. 1500",
                }
            ),

            "thumbnail": forms.ClearableFileInput(
                attrs={
                    "class": (
                        "block w-full text-sm text-gray-500 "
                        "file:mr-3 file:py-2 file:px-3 "
                        "file:border file:border-gray-300 "
                        "file:rounded-md file:text-sm "
                        "file:font-medium file:bg-white "
                        "file:text-gray-700 "
                        "hover:file:bg-gray-50 "
                        "file:cursor-pointer"
                    ),
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": (
                        "w-4 h-4 rounded border-gray-300 "
                        "text-gray-900 focus:ring-gray-500"
                    ),
                }
            ),
        }


class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount

        fields = [
            "percentage",
            "starts_at",
            "ends_at",
            "is_active",
        ]

        widgets = {
            "percentage": forms.NumberInput(
                attrs={
                    "class": (
                        "block w-full rounded-md border border-gray-300 "
                        "px-3 py-2 text-sm text-gray-900 "
                        "focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
                    ),
                    "min": "0.01",
                    "max": "100",
                    "step": "0.01",
                    "placeholder": "e.g. 30",
                }
            ),

            "starts_at": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": (
                        "block w-full rounded-md border border-gray-300 "
                        "px-3 py-2 text-sm text-gray-900 "
                        "focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
                    ),
                },
                format="%Y-%m-%dT%H:%M",
            ),

            "ends_at": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": (
                        "block w-full rounded-md border border-gray-300 "
                        "px-3 py-2 text-sm text-gray-900 "
                        "focus:border-gray-500 focus:ring-1 focus:ring-gray-500"
                    ),
                },
                format="%Y-%m-%dT%H:%M",
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": (
                        "w-4 h-4 rounded border-gray-300 "
                        "text-gray-900 focus:ring-gray-500"
                    ),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The discount section itself is optional.
        self.fields["percentage"].required = False
        self.fields["starts_at"].required = False
        self.fields["ends_at"].required = False
        self.fields["is_active"].required = False

        self.fields["starts_at"].input_formats = [
            "%Y-%m-%dT%H:%M"
        ]

        self.fields["ends_at"].input_formats = [
            "%Y-%m-%dT%H:%M"
        ]

    def clean_percentage(self):
        percentage = self.cleaned_data.get("percentage")

        # Empty means there is no discount.
        if percentage in (None, ""):
            return None

        if percentage <= 0:
            raise forms.ValidationError(
                "Discount must be greater than 0%."
            )

        if percentage > 100:
            raise forms.ValidationError(
                "Discount cannot exceed 100%."
            )

        return percentage

    def clean(self):
        cleaned_data = super().clean()

        percentage = cleaned_data.get("percentage")
        starts_at = cleaned_data.get("starts_at")
        ends_at = cleaned_data.get("ends_at")

        # If no percentage was entered, treat the whole
        # discount form as unused.
        if percentage is None:
            return cleaned_data

        # If a discount percentage exists, validate dates.
        if starts_at and ends_at and starts_at >= ends_at:
            self.add_error(
                "ends_at",
                "End time must be after the start time."
            )

        return cleaned_data