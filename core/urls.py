from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('analyze/single/', views.analyze_single, name='analyze_single'),
    path('analyze/batch/', views.analyze_batch, name='analyze_batch'),
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),
    path('session/<int:session_id>/export/', views.export_session_csv, name='export_session_csv'),
    path('session/<int:session_id>/insights/', views.get_session_insights, name='get_session_insights'),
]
