from django.urls import path
from . import views

urlpatterns = [
    path('', views.accounts_list, name='accounts_list'),
    path('<int:account_id>/', views.account_detail, name='account_detail'),
]
