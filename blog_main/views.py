from django.shortcuts import render, redirect
from blogs.models import Category, Blogs
from .forms import RegistrationForm
from django.contrib import auth, messages
from django.contrib.auth.forms import AuthenticationForm


def home(request):
    categories = Category.objects.all()
    featured_post = Blogs.objects.filter(is_featured=True, status='published')
    posts = Blogs.objects.filter(is_featured=False, status='published')
    
    context = {
        'categories': categories,
        'featured_post': featured_post,
        'posts': posts
    }
    return render(request, 'home.html', context)

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful.")  # Add this line
            return redirect('login')  # Optionally redirect to login page instead
    else:
        form = RegistrationForm()
    
    context = {
        'form': form
    }
    return render(request, 'register.html', context)

# Login Function
def login(request):
    next_url = request.GET.get('next') or request.POST.get('next') or 'home'

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password")  # Add error message here
    else:
        form = AuthenticationForm()

    context = {
        'form': form,
        'next': next_url
    }
    return render(request, 'login.html', context)

def logout(request):
    auth.logout(request)
    return redirect('home')
