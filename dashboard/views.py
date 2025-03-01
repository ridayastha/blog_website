from django.shortcuts import render, redirect
from blogs.models import Category, Blogs
from django.contrib.auth.decorators import login_required
from .forms import CategoryForm, BlogPostForm
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify


# Create your views here.
@login_required(login_url='login')
def dashboard(request):
    category_counts = Category.objects.all().count()
    blogs_counts = Blogs.objects.all().count()
    context={
        'category_counts': category_counts,
        'blogs_counts': blogs_counts
    }

    return render(request, 'dashboard/dashboard.html', context)


def categories(request):
    return render(request, 'dashboard/categories.html')

def add_categories(request):
    if request.method=="POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')
        
    form = CategoryForm()
    context = {
        'form': form
    }
    return render(request, 'dashboard/add_categories.html', context)

def edit_categories(request,pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method=="POST":
        form=CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('categories')
        
    form = CategoryForm(instance=category)
    context = {
        'form': form,
        'category': category
    }
    return render(request, 'dashboard/edit_categories.html', context)

def delete_categories(request,pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect('categories')



def posts(request):
    posts = Blogs.objects.all()
    context = {
        'posts':posts
    }
    return render(request, 'dashboard/posts.html', context)

def add_posts(request):
    if request.method=="POST":
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            title = form.cleaned_data['title']
            post.slug = slugify(title)
            post.save()
            print("Successful")
            return redirect('posts')
        else:
            print(form.errors)
        
    form = BlogPostForm()
    context = {
        'form': form
    }
    return render(request, 'dashboard/add_posts.html', context)

def edit_posts(request, pk):
    post = get_object_or_404(Blogs, pk=pk)
    if request.method=="POST":
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            title = form.cleaned_data['title']
            post.slug = slugify(title)
            post.save()
            return redirect('posts')
    form = BlogPostForm(instance=post)
    context = {
        'form':form,
        'post':post
    }
    return render(request, 'dashboard/edit_posts.html', context)

def delete_posts(request, pk):
    post = get_object_or_404(Blogs, pk=pk)
    post.delete()
    return redirect('posts')