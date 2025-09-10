"""
URL configuration for coach project.

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
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('clients.urls')),  # mounts the clients app routes
    path('api/auth/token/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('api/auth/token/refresh/',
         TokenRefreshView.as_view(), name='token_refresh'),
    path('api/billing/', include('billing.urls')),
    # Consults app temporarily disabled until restored
    path('api/consults/', include('consults.urls')),
    path('api/exercises/', include('exercises.urls')),
    path('api/bookings/', include('bookings.urls')),
    path('api/workouts/', include('workouts.urls')),
    path('api/templates/', include('templates.urls')),
    path('api/rules/', include('rules.urls')),
    path('api/emails/', include('emails.urls')),
]



