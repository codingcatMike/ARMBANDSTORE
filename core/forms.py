from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django import forms
from django.contrib.auth.models import User
from .models import *

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

        
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }