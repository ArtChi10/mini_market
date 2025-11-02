from django import forms

class BuyForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, label="Количество")
