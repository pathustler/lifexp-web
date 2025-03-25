from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import Player  # Import Player model
# Create your views here.


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            #Redirect to index view in the main app, we are now in the users app
            return redirect('index')
        else:
            messages.error(request, "Invalid credentials")
    
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('login')



def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user
            Player.objects.create(user=user)  # Create a Player object for the user
            login(request, user)  # Log in the new user
            return redirect('main:index')  # Redirect after registration
    else:
        form = UserCreationForm()

    return render(request, 'users/register.html', {'form': form})
