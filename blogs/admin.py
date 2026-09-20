# from django.contrib import admin
# from . models import Category, Blogs

# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('id', 'category_name', 'created_at', 'updated_at')

# class BlogAdmin(admin.ModelAdmin):
#     list_display = ('id','title','category','author','blog_image','status','is_featured','created_at','updated_at')
#     prepopulated_fields = {'slug':('title',)}
#     search_fields = ('id','title','category__category_name','status')
#     list_editable = ('is_featured',)


# admin.site.register(Category, CategoryAdmin)
# admin.site.register(Blogs, BlogAdmin)

from django.contrib import admin
from django import forms
from .models import Category, Blogs, Comment, CommentReaction
from ckeditor.widgets import CKEditorWidget  # Import CKEditor widget

# Custom Form to use CKEditor
class BlogAdminForm(forms.ModelForm):
    blog_body = forms.CharField(widget=CKEditorWidget())  # Use CKEditor in the admin panel

    class Meta:
        model = Blogs
        fields = '__all__'

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name', 'created_at', 'updated_at')

class BlogAdmin(admin.ModelAdmin):
    form = BlogAdminForm  # Assign the custom form with CKEditor
    list_display = ('id', 'title', 'category', 'author', 'blog_image', 'status', 'is_featured', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('id', 'title', 'category__category_name', 'status')
    list_editable = ('is_featured',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Blogs, BlogAdmin)
admin.site.register(Comment)
admin.site.register(CommentReaction)

