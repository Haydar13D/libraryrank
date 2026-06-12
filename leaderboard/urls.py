
from django.urls import path
from django.views.generic import TemplateView
from . import views
from . import integration_views

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

    # Public Integration API (Secured by API Key)
    path('api/docs/', TemplateView.as_view(template_name='leaderboard/swagger.html'), name='swagger_ui'),
    path('api/v1/member/<str:member_id>/', integration_views.integration_member_detail, name='integration_member_detail'),
    path('api/v1/member/<str:member_id>/add_points/', integration_views.integration_add_points, name='integration_add_points'),
    path('api/v1/rewards/', integration_views.integration_rewards, name='integration_rewards'),
    path('api/v1/redeem/', integration_views.integration_redeem, name='integration_redeem'),

    # Exports
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
]
