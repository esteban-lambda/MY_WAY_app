from django.urls import path
from . import views

urlpatterns = [
    path('', views.contacts_list, name='contacts_list'),
    path('<int:contact_id>/', views.contact_detail, name='contact_detail'),
]
