"""
URL configuration for kuravote project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
admin.site.login_template = 'admin/login.html'  # Custom admin login template

urlpatterns = [
    # Django built-in admin panel
    path('admin/', admin.site.urls),

    # All KuraVote app URLs
    path('', include('election.urls')),
]

# Serve media files (candidate photos) during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
