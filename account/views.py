from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import get_language
from django.contrib import messages
from django.contrib import auth
from django.views import View

from .tasks import mail_send
from .user_crypt import decoder
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    ProfileForm,
    UserForm,
)

User = get_user_model()


def activate_user_account(request, signed_user=None):
    user, signature = decoder(request, signed_user)
    if user and signature:
        user.email_confirm = True
        user.save()
        return render(request, "email_verify_done.html", {"user": user})
    elif user:
        host = request.get_host()
        scheme = request.scheme
        lang = get_language()
        mail_send.delay(lang, scheme, host, user.id)
        return render(request, "email_verify_end_of_time.html")
    else:
        return render(request, "user_does_not_exist.html")


def signup(request):
    if request.method == "POST":
        user_form = CustomUserCreationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data["password1"])
            new_user.save()
            host = request.get_host()
            scheme = request.scheme
            mail_send.delay(scheme, host, new_user.id)
            return render(
                request, "registration/signup_done.html", {"new_user": new_user}
            )
    else:
        user_form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"user_form": user_form})


@login_required
def profile(request):
    if request.method == "POST":
        user_form = UserForm(request.POST, request.FILES, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Ваш профіль був успішно оновлений!")
            return render(
                request,
                "profile.html",
                {
                    "user_form": user_form,
                    "profile_form": profile_form,
                },
            )
        else:
            messages.error(request, "Будь-ласка виправте помилку нижче.")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(
        request, "profile.html", {"user_form": user_form, "profile_form": profile_form}
    )


class CustomLoginView(View):
    def get(self, request):
        if auth.get_user(request).is_authenticated:
            return redirect("/")
        else:
            form = CustomAuthenticationForm
            return render(request, "registration/login.html", {"form": form})

    def post(self, request):
        form = CustomAuthenticationForm(request, data=request.POST)

        if form.is_valid():
            auth.login(
                request,
                form.get_user(),
                backend="users.authenticate.CustomModelBackend",
            )
            next = request.session.get("referer", "/")
            if next == "/admin/login/" and request.user.is_staff:
                return redirect("/admin/")
            return redirect(next)

        return render(request, "registration/login.html", {"form": form})
