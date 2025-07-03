from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm
from app.models import Compte

# Create your views here.
def index(request):
    return render(request, "index.html")

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_staff = True
            user.save()
            # Crée un compte d'argent de poche pour l'utilisateur
            Compte.objects.create(
                name=user.username,
                client=user,
                manager=user,  # ou choisir un manager par défaut
                salary=0
            )
            login(request, user)
            messages.success(request, "Votre compte a été créé. Vous pouvez maintenant accéder à l'administration.")
            return redirect("index")
    else:
        form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})