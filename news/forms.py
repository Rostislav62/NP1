# forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm

from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User

class CustomUserChangeForm(UserChangeForm):
    ACCOUNT_TYPE_CHOICES = [(False, 'Simple'), (True, 'Premium')]
    USER_TYPE_CHOICES = [(False, 'Reader'), (True, 'Author')]

    # account_type = forms.ChoiceField(choices=ACCOUNT_TYPE_CHOICES, label="Account type", required=True, widget=forms.Select)
    # is_author = forms.ChoiceField(choices=USER_TYPE_CHOICES, label="User type", required=True, widget=forms.Select)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        self.fields['password'].help_text = 'Чтобы изменить пароль вернитесь на страницу Профиль и выберите Изменить пароль'

    def save(self, commit=True):
        user = super(CustomUserChangeForm, self).save(commit=False)
        if commit:
            user.save()  # Сохраняем изменения пользователя
        return user

class CustomUserCreationForm(UserCreationForm):
    # Определяем поля с выпадающими списками
    ACCOUNT_TYPE_CHOICES = [(False, 'Simple'), (True, 'Premium')]
    USER_TYPE_CHOICES = [(False, 'Reader'), (True, 'Author')]

    # account_type = forms.ChoiceField(choices=ACCOUNT_TYPE_CHOICES, label="Account type", required=True,
    #                                  widget=forms.Select)
    # is_author = forms.ChoiceField(choices=USER_TYPE_CHOICES, label="User type", required=True, widget=forms.Select)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.is_active = True
        user.set_password(self.cleaned_data['password1'])  # Сохраняем зашифрованный пароль
        if commit:
            user.save()
        return user
