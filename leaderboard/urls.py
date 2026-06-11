
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
    path('api/redeem/request-otp/', views.api_request_otp, name='api_request_otp'),
    path('api/redeem/confirm/', views.api_verify_otp_and_redeem, name='api_verify_otp_and_redeem'),

    # Seminar routes
    path('seminar/', views.seminar_page, name='seminar_page'),
    path('api/seminar/list/', views.api_seminar_list, name='api_seminar_list'),
    path('api/seminar/register/', views.api_register_seminar, name='api_register_seminar'),
    path('api/seminar/claim/', views.api_claim_seminar_attendance, name='api_claim_seminar_attendance'),

    # Exports
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
]
