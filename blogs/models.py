from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField  # Import CKEditor
import math
from django.utils.html import strip_tags

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
    blog_image = models.ImageField(upload_to='uploads/%Y/%m/%d', default='default.jpg')
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
    
    @property
    def read_time(self):
        text = strip_tags(self.blog_body)
        word_count = len(text.split())
        return max(1, math.ceil(word_count / 200))  # 200 words per minute
    
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blogs, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.CASCADE, related_name='replies'
    )
    comment = models.TextField(max_length=250)
    is_edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.comment

class CommentReaction(models.Model):
    LIKE = 1
    DISLIKE = -1
    VALUE_CHOICES = ((LIKE, 'Like'), (DISLIKE, 'Dislike'))

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reactions')
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'comment'], name='one_reaction_per_user_per_comment')
        ]

    def __str__(self):
        return f"{self.user} -> {self.comment_id}: {self.value}"
    