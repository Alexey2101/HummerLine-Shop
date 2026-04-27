from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product

INPUT_CLASS = 'w-full rounded-xl border border-border p-3 focus:ring-2 focus:ring-ember-500 outline-none bg-white'

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'phone_number', 'image']
        widgets = {
            'category': forms.Select(attrs={'class': 'w-full rounded-xl border border-border p-3 focus:ring-2 focus:ring-ember-500 outline-none'}),
            'name': forms.TextInput(attrs={'class': 'w-full rounded-xl border border-border p-3 focus:ring-2 focus:ring-ember-500 outline-none'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-xl border border-border p-3 focus:ring-2 focus:ring-ember-500 outline-none', 'rows': 4}),
            'price': forms.NumberInput(attrs={
                'class': 'w-full rounded-xl border border-border p-3 focus:ring-2 focus:ring-ember-500 outline-none numeric-only',
                'inputmode': 'decimal'
            }),
            'phone_number': forms.TextInput(attrs={'class': 'w-full rounded-xl border border-border p-3 focus:ring-2 focus:ring-ember-500 outline-none', 'placeholder': '+7 (999) 999-99-99'}),
            'image': forms.FileInput(attrs={'class': 'w-full rounded-xl border border-border p-3 focus:ring-2 focus:ring-ember-500 outline-none bg-white'}),
        }


class UserEditForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Email', widget=forms.EmailInput(attrs={'class': INPUT_CLASS}))
    username = forms.CharField(label='Никнейм', widget=forms.TextInput(attrs={'class': INPUT_CLASS}))

    class Meta:
        model = User
        fields = ['username', 'email']

