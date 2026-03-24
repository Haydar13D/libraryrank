
from django.urls import path
from . import views

app_name = 'leaderboard'

urlpatterns = [
    # Main page
    path('', views.index, name='index'),

    # JSON API endpoints
    path('api/overview/', views.api_overview, name='api_overview'),
    path('api/role/<str:role>/', views.api_role_leaderboard, name='api_role'),
    path('api/books/', views.api_books, name='api_books'),
    path('api/faculties/', views.api_faculties, name='api_faculties'),
    path('api/member/<str:member_id>/', views.api_member_detail, name='api_member'),
    path('api/pemustaka-teraktif/', views.api_pemustaka_teraktif, name='api_pemustaka_teraktif'),

    # Exports
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
]
