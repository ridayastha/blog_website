from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings
from blogs import views as BlogsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    path('category/', include('blogs.urls')),

    path('blogs/search/', BlogsView.search, name='search'),  # must come before slug-based URLs
    path('blogs/<slug:slug>/', BlogsView.blogs, name='blogs'),
    path('blogs/<slug:slug>/comment/', BlogsView.add_comment, name='add_comment'),

    # comment actions (these views live in blogs/views.py)
    path('comment/<int:comment_id>/react/<str:action>/', BlogsView.react_comment, name='react_comment'),
    path('comment/<int:comment_id>/edit/', BlogsView.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', BlogsView.delete_comment, name='delete_comment'),

    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('dashboard/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)