# notes/admin.py - DYNAMIC VERSION
from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, Course, Subject, Chapter

# ============================================================================
# 1. USER PROFILE ADMIN
# ============================================================================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_verified', 'otp_created_at')
    list_filter = ('email_verified',)
    search_fields = ('user__username', 'user__email')

# ============================================================================
# 2. COURSE ADMIN (Dynamic Management)
# ============================================================================
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'display_order', 'is_active', 'subject_count_display', 'created_at')
    list_filter = ('level', 'is_active')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('display_order', 'is_active')
    
    # Fields to show in add/edit form
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'level', 'description', 'thumbnail')
        }),
        ('Display Settings', {
            'fields': ('display_order', 'is_active')
        }),
    )
    
    def subject_count_display(self, obj):
        count = obj.subject_count()
        return format_html('<span style="color: {};">{}</span>', 
                          'green' if count > 0 else 'red', 
                          f"{count} subject{'s' if count != 1 else ''}")
    subject_count_display.short_description = 'Subjects'

# ============================================================================
# 3. SUBJECT ADMIN (Dynamic Management)
# ============================================================================
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'display_order', 'is_active', 'chapter_count_display', 'created_at')
    list_filter = ('course', 'is_active')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('display_order', 'is_active')
    
    # Fields to show in add/edit form
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'slug', 'description')
        }),
        ('Display Settings', {
            'fields': ('display_order', 'is_active')
        }),
    )
    
    def chapter_count_display(self, obj):
        count = obj.chapter_count()
        return format_html('<span style="color: {};">{}</span>', 
                          'green' if count > 0 else 'red', 
                          f"{count} chapter{'s' if count != 1 else ''}")
    chapter_count_display.short_description = 'Chapters'

# ============================================================================
# 4. CHAPTER ADMIN (Dynamic Management)
# ============================================================================
@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'display_order', 'is_active', 'created_at')
    list_filter = ('subject', 'is_active')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('display_order', 'is_active')
    
    # Fields to show in add/edit form
    fieldsets = (
        ('Basic Information', {
            'fields': ('subject', 'title', 'slug', 'content')
        }),
        ('Display Settings', {
            'fields': ('display_order', 'is_active')
        }),
    )