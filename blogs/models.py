from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField  # Import CKEditor

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.category_name

STATUS_CHOICE = (
    ('draft', 'Draft'),
    ('published', 'Published')
)

class Blogs(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True) # slug is a part of an url that identifies the particular page on a website.
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    blog_image = models.ImageField(upload_to='uploads/%Y/%m/%d')
    short_description = models.TextField(max_length=1000)
    blog_body = RichTextField()
    status = models.CharField(max_length=100, choices = STATUS_CHOICE, default='draft')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'blogs'
    
    def __str__(self):
        return self.title
    
    


    