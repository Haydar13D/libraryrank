import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryrank.settings')
django.setup()

from django.db import connections

try:
    cursor = connections['koha'].cursor()
    cursor.execute("SELECT borrowernumber, cardnumber, surname, firstname, categorycode, branchcode, lost, dateenrolled FROM borrowers WHERE cardnumber = 'L200230051' OR userid = 'L200230051'")
    row = cursor.fetchone()
    if row:
        print('KOHA DATA:', row)
        
        # Check if it matches .env categories
        from django.conf import settings
        cat_upper = (row[4] or '').upper()
        student_cats  = [c.upper() for c in settings.KOHA_STUDENT_CATEGORIES]
        lecturer_cats = [c.upper() for c in settings.KOHA_LECTURER_CATEGORIES]
        staff_cats    = [c.upper() for c in settings.KOHA_STAFF_CATEGORIES]
        
        if cat_upper in student_cats:
            print('Role: student')
        elif cat_upper in lecturer_cats:
            print('Role: lecturer')
        elif cat_upper in staff_cats:
            print('Role: staff')
        else:
            print(f'WARNING: Category code "{cat_upper}" is NOT in .env list!')
    else:
        print('No data found for L200230051 in Koha')
except Exception as e:
    print('ERROR:', e)
