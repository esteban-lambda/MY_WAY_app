from django.urls import path
from . import views

urlpatterns = [
    path('pipeline/', views.pipeline_view, name='pipeline'),
    path('pipeline/update/<int:deal_id>/', views.update_deal_stage, name='update_deal_stage'),
]