from django.urls import path
from . import views

urlpatterns = [
    # ... existing URL patterns ...
    path('delete-account/', views.delete_user, name='delete_account'),
] 