from django.urls import path
from offline_app import views

urlpatterns = [
    path('create_member/', views.create_member),
]


