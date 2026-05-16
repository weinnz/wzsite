"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
#from django.conf.urls import url
from web import views as web_views
from blog import views as blog_views
from gallery import views as gallery_views
from recipe import views as recipe_views
from works import views as works_views
from notes import views as notes_views
from django.views import static ##新增
from django.conf import settings ##新增
from django.urls import re_path as url


handler404 = web_views.handler404

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}, name='static'),
    path('', web_views.index),
    path('contact/', web_views.contact),
    path('blog/details/<slug:blog_id>', blog_views.blog_detail),
    path('blog/', blog_views.blog),
    path('gallery/details/<slug:gallery_id>', gallery_views.gallery_detail),
    path('gallery/', gallery_views.gallery),
    path('recipe/', recipe_views.recipe),
    path('notes/details/<slug:note_id>', notes_views.note_detail),
    path('notes/', notes_views.notes),
    path('works/', works_views.works),
    path('search/', web_views.search),

    # ajax task
    path('contact/task/leave-message/', web_views.leave_message),

    path('blog/task/get-blog-by-smile/', blog_views.get_blog),
    path('blog/task/like-toggle/', blog_views.like_toggle),
    path('blog/task/post-comment/', blog_views.post_comment),

    path('notes/task/like-toggle/', notes_views.like_toggle),
    path('notes/task/post-comment/', notes_views.post_comment),
    

]
