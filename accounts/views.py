from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .forms import RegistrationForm, LoginForm
from .models import CustomUser


from django.contrib.auth.backends import ModelBackend


class CustomBackend(ModelBackend):
    """
    Custom Backend Authentication for validating users based on email rather
    than conventional django auth (username)
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(
                email=username, is_active=True, is_superuser=False
            )
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None


# Creating a new user
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("accounts:home")  # Redirect to the user's profile page
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


# Login view for registered users
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username_or_email, password=password)
            if user is not None:
                login(request, user)
                return redirect("accounts:home")  # Redirect to the user's profile page
            else:
                messages.error(request, "Invalid login credentials. Please try again.")

    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


@login_required
def home(request):
    api_key = settings.GOOGLE_MAPS_API_KEY
    return render(request, "maps/home.html", {"api_key": api_key})


def logout_view(request):
    logout(request)
    return redirect("accounts:login")
