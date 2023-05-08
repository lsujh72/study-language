from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    UsernameField,
    AuthenticationForm,
)
from django.utils.text import capfirst

from .models import Profile

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=False, widget=forms.EmailInput(attrs={"placeholder": "Введіть email"})
    )
    password1 = forms.CharField(
        label=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "placeholder": "Введіть пароль"}
        ),
        strip=False,
    )
    password2 = forms.CharField(
        label=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "placeholder": "Повторіть пароль"}
        ),
        strip=False,
    )
    use_required_attribute = False

    class Meta(UserCreationForm):
        model = User
        fields = ("email", "first_name", "last_name")


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm):
        model = User
        fields = ("email", "first_name", "last_name")


class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={"autofocus": True}))
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    error_messages = {
        "invalid_login": "Будь ласка введіть правильну електронну адресу та пароль.",
        "inactive": "Цей акаунт не активований.",
    }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("phone", "street", "postal_code", "city", "region", "province")


class AddUserForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
