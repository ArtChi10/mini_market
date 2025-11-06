from django import forms
from .models import Product

class ProductStudentForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["title", "category", "price", "stock", "image", "description", "ascii_art"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "ascii_art": forms.Textarea(attrs={"rows": 6, "placeholder": "Нарисуй символами :)"}),
        }

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise forms.ValidationError("Цена должна быть больше нуля.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data["stock"]
        if stock < 0:
            raise forms.ValidationError("Остаток не может быть отрицательным.")
        return stock


class ProductClaimForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["description", "image"]  # правим описание и картинку

    def clean_image(self):
        img = self.cleaned_data.get("image")
        if img and img.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Файл слишком большой (макс. 5 МБ).")
        return img