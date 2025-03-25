from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm
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
            error= "Invalid credentials"
            messages.error(request, "Invalid credentials")
    
    return render(request, 'users/login.html',
                  {'error': error if 'error' in locals() else None})

def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('login')



def register_view(request):
    errors = None
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user, now with the email
            # displayname is a field in the form in the html page but not in the django form, i want to extract that data using request.POST
            displayname = request.POST['displayname']  # Save the display
            p = Player(user=user,username=user.username,fullname=displayname, email=user.email)  # Create a Player object for the user
            p.save()
            user.save()
            print(p)
            print(user)
            login(request, user)  # Log in the new user
            return redirect('index')  # Redirect after registration
        
        else:
            erros = form.errors
            print("invalid form")
            print(form.errors)
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form, 'errors': errors})