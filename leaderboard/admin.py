from django.contrib import admin
from .models import Member, Faculty, Book, Visit, BorrowRecord


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'color']
    search_fields = ['name', 'code']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['member_id', 'name', 'role', 'faculty', 'department', 'visit_count', 'is_active']
    list_filter = ['role', 'faculty', 'is_active']
    search_fields = ['member_id', 'name', 'faculty__name', 'department']
    list_editable = ['is_active']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['isbn', 'title', 'author', 'category', 'faculty', 'borrow_count']
    list_filter = ['category', 'faculty']
    search_fields = ['isbn', 'title', 'author']


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ['member', 'visited_at', 'purpose']
    list_filter = ['visited_at', 'member__role', 'member__faculty']
    search_fields = ['member__name', 'member__member_id']
    date_hierarchy = 'visited_at'


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ['member', 'book', 'borrowed_at', 'due_date', 'status']
    list_filter = ['status', 'borrowed_at', 'member__role']
    search_fields = ['member__name', 'book__title']
    date_hierarchy = 'borrowed_at'
