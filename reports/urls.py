from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='dashboard'),
    path('sales/', views.sales_report, name='sales'),
    path('pipeline/', views.pipeline_report, name='pipeline'),
    path('activity/', views.activity_report, name='activity'),
    path('accounts/', views.accounts_report, name='accounts'),
]
