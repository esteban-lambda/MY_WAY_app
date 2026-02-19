from django.urls import path
from . import views

app_name = 'timeline'

urlpatterns = [
    path('', views.timeline_view, name='timeline'),
    path('account/<int:account_id>/', views.timeline_account, name='account'),
    path('contact/<int:contact_id>/', views.timeline_contact, name='contact'),
    path('deal/<int:deal_id>/', views.timeline_deal, name='deal'),
]
