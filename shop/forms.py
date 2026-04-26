from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product, DeliveryCompany

INPUT_CLASS = 'w-full rounded-xl border border-border p-3 focus:ring-2 focus:ring-ember-500 outline-none bg-white'

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)


class DeliveryCompanyRegistrationForm(UserCreationForm):
    """Combined form: creates a User account + DeliveryCompany profile."""
    email = forms.EmailField(required=True, label='Email')
    company_name = forms.CharField(max_length=200, label='Название компании',
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'ООО «Быстрая доставка»'}))
    phone = forms.CharField(max_length=20, label='Телефон',
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': '+7 (700) 000-00-00'}))
    regions = forms.CharField(label='Регионы доставки',
        widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Алматы, Астана, Шымкент'}))
    transport_types = forms.ChoiceField(choices=DeliveryCompany.TRANSPORT_CHOICES, label='Основной транспорт',
        widget=forms.Select(attrs={'class': INPUT_CLASS}))
    price_per_km = forms.DecimalField(max_digits=8, decimal_places=2, label='Цена за км (₸)',
        widget=forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': '150'}))
    description = forms.CharField(required=False, label='Описание услуг',
        widget=forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 3,
                                     'placeholder': 'Кратко опишите ваши услуги и преимущества...'}))
    logo = forms.ImageField(required=False, label='Логотип',
        widget=forms.FileInput(attrs={'class': INPUT_CLASS}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2']


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

