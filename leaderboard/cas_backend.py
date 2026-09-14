import logging
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import connections
from django_cas_ng.backends import CASBackend

logger = logging.getLogger(__name__)
UserModel = get_user_model()

class LibrarianCASBackend(CASBackend):
    """
    Custom CAS SSO Authentication Backend for LibraryRank.
    Restricts Admin Login STRICTLY to Librarians (Pustakawan / Staf Perpustakaan).
    """

    def is_librarian(self, username, attributes=None):
        """
        Check if the given username corresponds to a Librarian in Koha database.
        Strict check: categorycode in Koha MUST be 'LIBRARIAN'.
        """
        attributes = attributes or {}
        user_clean = username.strip().upper()

        # 1. Query Koha database for patron category
        try:
            with connections['koha'].cursor() as cursor:
                cursor.execute(
                    """
                    SELECT categorycode, branchcode, surname, firstname, email 
                    FROM borrowers 
                    WHERE UPPER(userid) = %s OR UPPER(cardnumber) = %s
                    LIMIT 1
                    """,
                    [user_clean, user_clean]
                )
                row = cursor.fetchone()
                if row:
                    cat = (row[0] or '').upper()
                    librarian_cats = [c.upper() for c in getattr(settings, 'KOHA_LIBRARIAN_CATEGORIES', ['LIBRARIAN'])]
                    
                    # Strictly check if categorycode is LIBRARIAN
                    if cat in librarian_cats:
                        return True, {
                            'first_name': row[3] or '',
                            'last_name': row[2] or '',
                            'email': row[4] or '',
                            'category': cat,
                        }
                    else:
                        # Found in Koha but NOT a Librarian (e.g. STAF1, STAF2, STD1, STD2, TC1, etc.)
                        logger.info(f"User {user_clean} rejected: Koha category is '{cat}', not 'LIBRARIAN'.")
                        return False, {'category': cat}
        except Exception as e:
            logger.warning(f"Koha DB check error during CAS auth: {e}")

        # 2. Check CAS attributes (e.g. Unit / Department / EmployeeType specifically for Perpustakaan)
        librarian_keywords = ['perpustakaan', 'library', 'pustakawan', 'librarian']
        for key, val in attributes.items():
            val_str = str(val).lower()
            if any(kw in val_str for kw in librarian_keywords):
                return True, {
                    'first_name': attributes.get('givenName') or attributes.get('cn') or '',
                    'last_name': attributes.get('sn') or '',
                    'email': attributes.get('mail') or attributes.get('email') or '',
                }

        return False, {}

    def authenticate(self, request, ticket=None, service=None):
        user = super().authenticate(request, ticket=ticket, service=service)
        if not user:
            return None

        attributes = getattr(request, 'session', {}).get('attributes', {}) if request else {}
        is_lib, info = self.is_librarian(user.username, attributes)

        if is_lib:
            # Grant staff and superuser permissions for Admin Panel access
            user.is_staff = True
            user.is_superuser = True
            
            # Sync user profile info if provided
            if info.get('first_name') and not user.first_name:
                user.first_name = str(info['first_name'])
            if info.get('last_name') and not user.last_name:
                user.last_name = str(info['last_name'])
            if info.get('email') and not user.email:
                user.email = str(info['email'])
                
            user.save()
            return user
        else:
            # Non-librarian detected: Revoke permissions and REJECT admin login
            logger.warning(f"Rejected CAS login for non-librarian user: {user.username} (Category: {info.get('category')})")
            user.is_staff = False
            user.is_superuser = False
            user.save()
            
            if request:
                from django.contrib import messages
                messages.error(
                    request, 
                    f"Akses Ditolak: Akun '{user.username}' terdaftar sebagai karyawan umum ({info.get('category', 'Non-Librarian')}), bukan Pustakawan (LIBRARIAN). Hanya Pustakawan yang diizinkan mengakses panel admin."
                )
            return None
