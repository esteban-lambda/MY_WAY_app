from django.urls import path
from . import views

urlpatterns = [
    path('', views.interactions_list, name='interactions_list'),
    path('<int:interaction_id>/', views.interaction_detail, name='interaction_detail'),
]
