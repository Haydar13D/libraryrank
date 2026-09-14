import urllib.parse as urllib_parse
from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_cas_ng.views import (
    LogoutView as BaseCASLogoutView,
    clean_next_page,
    get_cas_client,
    get_protocol,
    get_redirect_url,
    ProxyGrantingTicket,
    SessionTicket,
    cas_user_logout,
    SESSION_KEY_MAXLENGTH,
)

@method_decorator(csrf_exempt, name='dispatch')
class CASLogoutView(BaseCASLogoutView):
    """
    Custom CAS Logout View that supports both GET and POST requests.
    Prevents HTTP 405 Method Not Allowed when Django Admin logout form submits via POST.
    Logs out user locally and redirects to CAS Central Logout to terminate SSO session.
    """

    def handle_logout(self, request: HttpRequest) -> HttpResponse:
        next_url = getattr(
            settings,
            "CAS_LOGOUT_NEXT_PAGE",
            request.GET.get("next") or request.POST.get("next") or "/admin/login/",
        )
        next_page = clean_next_page(request, next_url)

        session_key = None
        if request.session and request.session.session_key:
            session_key = request.session.session_key[:SESSION_KEY_MAXLENGTH]

        try:
            st = SessionTicket.objects.get(session_key=session_key)
            ticket = st.ticket
        except SessionTicket.DoesNotExist:
            ticket = None

        # Send logout signal
        cas_user_logout.send(
            sender="manual",
            user=request.user,
            session=request.session,
            ticket=ticket,
        )

        # Clean session tickets
        if session_key:
            ProxyGrantingTicket.objects.filter(session_key=session_key).delete()
            SessionTicket.objects.filter(session_key=session_key).delete()

        # Logout from Django session
        auth_logout(request)

        next_page = next_page or get_redirect_url(request) or "/admin/login/"
        
        logout_completely = getattr(settings, "CAS_LOGOUT_COMPLETELY", True)
        if logout_completely:
            if next_page.lower().startswith("https://") or next_page.lower().startswith("http://"):
                redirect_url = next_page
            else:
                if hasattr(settings, 'CAS_ROOT_PROXIED_AS') and settings.CAS_ROOT_PROXIED_AS:
                    protocol, host, _, _, _, _ = urllib_parse.urlparse(settings.CAS_ROOT_PROXIED_AS)
                else:
                    protocol = get_protocol(request)
                    host = request.get_host()

                redirect_url = urllib_parse.urlunparse(
                    (protocol, host, next_page, '', '', ''),
                )
            try:
                client = get_cas_client(request=request)
                return HttpResponseRedirect(client.get_logout_url(redirect_url))
            except Exception:
                return HttpResponseRedirect(next_page)

        return HttpResponseRedirect(next_page)

    def get(self, request: HttpRequest) -> HttpResponse:
        return self.handle_logout(request)

    def post(self, request: HttpRequest) -> HttpResponse:
        return self.handle_logout(request)
