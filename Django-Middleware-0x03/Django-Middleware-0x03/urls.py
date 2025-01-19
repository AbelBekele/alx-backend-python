# messaging_app/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from chats.auth import CustomTokenObtainPairView

from django.shortcuts import redirect

def redirect_to_api(request):
    return redirect('api/')

urlpatterns = [
    path('', redirect_to_api),
    path('admin/', admin.site.urls),
    path('api/', include('chats.urls')),
]

