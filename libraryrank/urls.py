from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
import django_cas_ng.views as cas_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── CAS SSO ──
    # Note: django-cas-ng does NOT have a urls module — routes are added manually
    path('accounts/login/',    cas_views.LoginView.as_view(),  name='cas_ng_login'),
    path('accounts/logout/',   cas_views.LogoutView.as_view(), name='cas_ng_logout'),
    path('accounts/callback/', cas_views.CallbackView.as_view(), name='cas_ng_callback'),

    # ── Local dev login (only used when CAS_LOCAL_DEV=True) ──
    path('accounts/dev-login/',  auth_views.LoginView.as_view(
        template_name='leaderboard/dev_login.html'
    ), name='dev_login'),
    path('accounts/dev-logout/', auth_views.LogoutView.as_view(
        next_page='/'
    ), name='dev_logout'),

    # ── App ──
    path('', include('leaderboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
