from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')),
    path('matches/', include('matches.urls')),
    path('chat/', include('chat.urls')),
    path('live/', include('live.urls')),
    path('social/', include('social.urls')),
    path('', user_views.home, name='home'),
    path('', include('profiles.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)