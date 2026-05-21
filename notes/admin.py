# notes/admin.py
import csv
from datetime import date, timedelta

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import OuterRef, Exists
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Chapter, Course, Payment, PremiumSubscription, Subject, UserProfile


# ============================================================================
# PATCH DEFAULT ADMIN SITE — branding + dashboard context
# ============================================================================

from django.contrib.admin import site as admin_site

admin_site.site_header = "Notes Admin"
admin_site.site_title  = "Notes Admin"
admin_site.index_title = "Dashboard"

_original_index = admin_site.__class__.index

def _custom_index(self, request, extra_context=None):
    today            = timezone.now()
    three_days_later = today.date() + timedelta(days=3)
    thirty_days_ago  = today - timedelta(days=30)
    seven_days_ago   = today - timedelta(days=7)

    approved_payment_ids = PremiumSubscription.objects.filter(
        payment=OuterRef('pk'), is_active=True
    )
    pending_qs = Payment.objects.annotate(
        has_sub=Exists(approved_payment_ids)
    ).filter(has_sub=False)

    total_users   = User.objects.count()
    premium_users = User.objects.filter(profile__is_premium=True).count()

    expiring_subs = PremiumSubscription.objects.filter(
        is_active=True,
        ends_at__range=[today.date(), three_days_later]
    ).select_related('user').order_by('ends_at')

    extra_context = extra_context or {}
    extra_context.update({
        'total_users':            total_users,
        'premium_users':          premium_users,
        'free_users':             total_users - premium_users,
        'premium_percentage':     round(premium_users / total_users * 100, 1) if total_users else 0,
        'new_users_month':        User.objects.filter(date_joined__gte=thirty_days_ago).count(),
        'active_users_week':      User.objects.filter(last_login__gte=seven_days_ago).count(),
        'expiring_soon_count':    expiring_subs.count(),
        'pending_payments_count': pending_qs.count(),
        'total_courses':          Course.objects.filter(is_active=True).count(),
        'total_chapters':         Chapter.objects.filter(is_active=True).count(),
        'estimated_revenue':      premium_users * 1000,
        'monthly_revenue':        PremiumSubscription.objects.filter(
                                      started_at__gte=thirty_days_ago
                                  ).count() * 1000,
        'pending_payment_list':   pending_qs.select_related('user').order_by('-submitted_at')[:6],
        'expiring_subs_list':     expiring_subs[:6],
    })
    return _original_index(self, request, extra_context)

admin_site.__class__.index = _custom_index


# ============================================================================
# SYSTEM REPORT VIEW
# ============================================================================

def system_report_view(request):
    today           = timezone.now()
    thirty_days_ago = today - timedelta(days=30)
    seven_days_ago  = today - timedelta(days=7)

    total_users   = User.objects.count()
    premium_users = User.objects.filter(profile__is_premium=True).count()

    approved_payment_ids = PremiumSubscription.objects.filter(
        payment=OuterRef('pk'), is_active=True
    )
    total_payments    = Payment.objects.count()
    approved_payments = Payment.objects.annotate(
        has_sub=Exists(approved_payment_ids)
    ).filter(has_sub=True).count()

    context = {
        'report_date':         today,
        'total_users':         total_users,
        'premium_users':       premium_users,
        'free_users':          total_users - premium_users,
        'new_users':           User.objects.filter(date_joined__gte=thirty_days_ago).count(),
        'active_users':        User.objects.filter(last_login__gte=seven_days_ago).count(),
        'premium_percentage':  round(premium_users / total_users * 100, 1) if total_users else 0,
        'active_premium':      PremiumSubscription.objects.filter(
                                   is_active=True, ends_at__gte=today.date()
                               ).count(),
        'expiring_soon':       PremiumSubscription.objects.filter(
                                   is_active=True,
                                   ends_at__gte=today.date(),
                                   ends_at__lte=today.date() + timedelta(days=3)
                               ).count(),
        'total_payments':      total_payments,
        'approved_payments':   approved_payments,
        'pending_payments':    total_payments - approved_payments,
        'approval_percentage': round(approved_payments / total_payments * 100, 1) if total_payments else 0,
        'total_courses':       Course.objects.filter(is_active=True).count(),
        'total_subjects':      Subject.objects.filter(is_active=True).count(),
        'total_chapters':      Chapter.objects.filter(is_active=True).count(),
        'estimated_revenue':   premium_users * 1000,
        'monthly_revenue':     PremiumSubscription.objects.filter(
                                   started_at__gte=thirty_days_ago
                               ).count() * 1000,
        'thirty_days_ago':     thirty_days_ago.date(),
        'seven_days_ago':      seven_days_ago.date(),
    }
    return render(request, 'admin/system_report.html', context)


# ============================================================================
# HELPER — safe days remaining (never returns None)
# ============================================================================

def _days_remaining(obj):
    try:
        val = getattr(obj, 'days_remaining', None)
        if val is not None:
            return int(val)
        if obj.ends_at:
            return max((obj.ends_at - date.today()).days, 0)
    except Exception:
        pass
    return 0


# ============================================================================
# 1. CUSTOM USER ADMIN
# ============================================================================

class UserProfileInline(admin.StackedInline):
    model               = UserProfile
    can_delete          = False
    verbose_name_plural = 'Profile'
    fields              = ('email_verified', 'is_premium', 'otp_created_at')
    readonly_fields     = ('otp_created_at',)


admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines       = (UserProfileInline,)
    list_display  = ('username', 'email', 'first_name', 'last_name',
                     'is_premium_display', 'is_staff', 'date_joined')
    list_filter   = ('is_staff', 'is_superuser', 'profile__is_premium', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering      = ('-date_joined',)

    def is_premium_display(self, obj):
        try:
            if obj.profile.is_premium:
                return mark_safe('<span style="color:#3B6D11;font-weight:500">&#10003; Premium</span>')
            return mark_safe('<span style="color:#aaa">Free</span>')
        except Exception:
            return '—'
    is_premium_display.short_description = 'Plan'

    def make_staff(self, request, queryset):
        queryset.update(is_staff=True)
        self.message_user(request, f"Granted staff access to {queryset.count()} user(s)")
    make_staff.short_description = "Grant staff (admin) access"

    actions = ['make_staff']


# ============================================================================
# 2. USER PROFILE ADMIN
# ============================================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'user_email', 'email_verified', 'is_premium', 'otp_created_at')
    list_filter   = ('email_verified', 'is_premium')
    search_fields = ('user__username', 'user__email')
    ordering      = ('-otp_created_at',)

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def verify_emails(self, request, queryset):
        queryset.update(email_verified=True)
        self.message_user(request, f"Verified {queryset.count()} email(s)")
    verify_emails.short_description = "Mark emails as verified"

    def revoke_premium_profiles(self, request, queryset):
        queryset.update(is_premium=False)
        self.message_user(request, f"Revoked premium from {queryset.count()} profile(s)")
    revoke_premium_profiles.short_description = "Revoke premium flag"

    actions = ['verify_emails', 'revoke_premium_profiles']


# ============================================================================
# 3. COURSE ADMIN
# ============================================================================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display        = ('title', 'level', 'display_order', 'is_active',
                           'subject_count_display', 'created_at')
    list_filter         = ('level', 'is_active')
    search_fields       = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable       = ('display_order', 'is_active')
    ordering            = ('display_order',)

    fieldsets = (
        ('Basic information', {
            'fields': ('title', 'slug', 'level', 'description', 'thumbnail')
        }),
        ('Display settings', {
            'fields': ('display_order', 'is_active')
        }),
    )

    def subject_count_display(self, obj):
        count = obj.subject_count()
        color = '#3B6D11' if count > 0 else '#A32D2D'
        return format_html(
            '<span style="color:{};font-weight:500">{} subject{}</span>',
            color, count, 's' if count != 1 else ''
        )
    subject_count_display.short_description = 'Subjects'


# ============================================================================
# 4. SUBJECT ADMIN
# ============================================================================

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display        = ('title', 'course', 'display_order', 'is_active',
                           'chapter_count_display', 'created_at')
    list_filter         = ('course', 'is_active')
    search_fields       = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable       = ('display_order', 'is_active')
    ordering            = ('course', 'display_order')

    fieldsets = (
        ('Basic information', {
            'fields': ('course', 'title', 'slug', 'description')
        }),
        ('Display settings', {
            'fields': ('display_order', 'is_active')
        }),
    )

    def chapter_count_display(self, obj):
        count = obj.chapter_count()
        color = '#3B6D11' if count > 0 else '#A32D2D'
        return format_html(
            '<span style="color:{};font-weight:500">{} chapter{}</span>',
            color, count, 's' if count != 1 else ''
        )
    chapter_count_display.short_description = 'Chapters'


# ============================================================================
# 5. CHAPTER ADMIN
# ============================================================================

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display        = ('title', 'subject', 'has_pdf', 'has_video',
                           'display_order', 'is_active', 'created_at')
    search_fields       = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable       = ('display_order', 'is_active')
    list_filter         = ('subject__course', 'is_active')
    ordering            = ('subject', 'display_order')

    fieldsets = (
        ('Basic information', {
            'fields': ('subject', 'title', 'slug', 'content')
        }),
        ('Chapter resources', {
            'fields': ('pdf_file', 'video_url')
        }),
        ('Display settings', {
            'fields': ('display_order', 'is_active')
        }),
    )

    def has_pdf(self, obj):
        return bool(obj.pdf_file)
    has_pdf.boolean = True
    has_pdf.short_description = 'PDF'

    def has_video(self, obj):
        return bool(obj.video_url)
    has_video.boolean = True
    has_video.short_description = 'Video'


# ============================================================================
# 6. PAYMENT ADMIN
# ============================================================================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display    = ('user', 'email_display', 'submitted_at',
                       'screenshot_preview', 'payment_status', 'payment_approve')
    list_filter     = ('submitted_at',)
    search_fields   = ('user__username', 'user__email', 'email')
    readonly_fields = ('submitted_at', 'screenshot_preview_large')
    ordering        = ('-submitted_at',)

    def email_display(self, obj):
        try:
            return obj.email if getattr(obj, 'email', None) else obj.user.email
        except Exception:
            return '—'
    email_display.short_description = 'Email'

    def screenshot_preview(self, obj):
        try:
            if obj.screenshot:
                return format_html(
                    '<a href="{}" target="_blank">'
                    '<img src="{}" style="height:40px;border-radius:4px;border:1px solid #eee"/>'
                    '</a>',
                    obj.screenshot.url, obj.screenshot.url
                )
        except Exception:
            pass
        return '—'
    screenshot_preview.short_description = 'Screenshot'

    def screenshot_preview_large(self, obj):
        try:
            if obj.screenshot:
                return format_html(
                    '<a href="{}" target="_blank">'
                    '<img src="{}" style="max-width:400px;border-radius:8px"/>'
                    '</a>',
                    obj.screenshot.url, obj.screenshot.url
                )
        except Exception:
            pass
        return 'No screenshot uploaded'
    screenshot_preview_large.short_description = 'Payment screenshot'

    def payment_status(self, obj):
        # NOTE: method name avoids 'status_display' which conflicts with Django internals
        try:
            has_active = PremiumSubscription.objects.filter(
                payment=obj, is_active=True, ends_at__gte=date.today()
            ).exists()
            if has_active:
                return mark_safe(
                    '<span style="background:#EAF3DE;color:#3B6D11;padding:3px 10px;'
                    'border-radius:12px;font-size:11px;font-weight:500">Approved</span>'
                )
        except Exception:
            pass
        return mark_safe(
            '<span style="background:#FAEEDA;color:#854F0B;padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:500">Pending</span>'
        )
    payment_status.short_description = 'Status'

    def payment_approve(self, obj):
        # NOTE: method name avoids 'approve_action' which can conflict
        try:
            has_active = PremiumSubscription.objects.filter(
                user=obj.user, is_active=True, ends_at__gte=date.today()
            ).exists()
            if has_active:
                return mark_safe(
                    '<span style="color:#3B6D11;font-size:12px">&#10003; Already premium</span>'
                )
        except Exception:
            pass
        return mark_safe(
            f'<a href="/admin/notes/payment/{obj.id}/approve/" '
            f'style="background:#1a1a2e;color:#fff;padding:4px 12px;border-radius:6px;'
            f'font-size:12px;text-decoration:none">Approve</a>'
        )
    payment_approve.short_description = 'Action'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:payment_id>/approve/',
                 self.admin_site.admin_view(self.approve_payment),
                 name='payment_approve'),
        ]
        return custom_urls + urls

    def approve_payment(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id)
            has_active = PremiumSubscription.objects.filter(
                user=payment.user, is_active=True, ends_at__gte=date.today()
            ).exists()
            if has_active:
                messages.warning(
                    request, f"⚠ {payment.user.username} already has active premium."
                )
            else:
                PremiumSubscription.objects.create(
                    user=payment.user,
                    ends_at=date.today() + timedelta(days=30),
                    payment=payment,
                    admin_notes=f"Approved payment #{payment.id}",
                    is_active=True
                )
                try:
                    profile = payment.user.profile
                    profile.is_premium = True
                    profile.save(update_fields=['is_premium'])
                except Exception:
                    pass
                messages.success(
                    request,
                    f"✓ Premium activated for {payment.user.username} (30 days)."
                )
        except Payment.DoesNotExist:
            messages.error(request, "Payment not found.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

        return redirect('/admin/notes/payment/')

    def make_premium(self, request, queryset):
        created = 0
        for payment in queryset:
            try:
                existing = PremiumSubscription.objects.filter(user=payment.user).first()
                if existing:
                    base = existing.ends_at if existing.ends_at >= date.today() else date.today()
                    existing.ends_at   = base + timedelta(days=30)
                    existing.is_active = True
                    existing.payment   = payment
                    existing.save()
                else:
                    PremiumSubscription.objects.create(
                        user=payment.user,
                        ends_at=date.today() + timedelta(days=30),
                        payment=payment,
                        admin_notes=f'Bulk approved from Payment #{payment.id}',
                        is_active=True
                    )
                    created += 1
                try:
                    payment.user.profile.is_premium = True
                    payment.user.profile.save(update_fields=['is_premium'])
                except Exception:
                    pass
            except Exception as e:
                messages.error(request, f"Error with payment {payment.id}: {str(e)}")
        self.message_user(request, f"✓ Created/updated premium for {created} user(s)")
    make_premium.short_description = "Approve & activate premium"

    actions = ['make_premium']


# ============================================================================
# 7. PREMIUM SUBSCRIPTION ADMIN
# ============================================================================

@admin.register(PremiumSubscription)
class PremiumSubscriptionAdmin(admin.ModelAdmin):
    list_display    = ('user', 'email_column', 'started_at', 'ends_at',
                       'days_left_formatted', 'sub_status', 'sub_method')
    list_filter     = ('is_active', 'ends_at')
    search_fields   = ('user__username', 'user__email', 'admin_notes')
    readonly_fields = ('started_at', 'days_left_display')
    ordering        = ('ends_at',)
    list_per_page   = 50
    actions         = ['extend_30_days', 'revoke_premium', 'export_to_csv']

    change_list_template = 'admin/notes/premiumsubscription/change_list.html'

    fieldsets = (
        ('Basic info', {
            'fields': ('user', 'payment', 'admin_notes')
        }),
        ('Subscription dates', {
            'fields': ('started_at', 'ends_at', 'is_active')
        }),
        ('Status', {
            'fields': ('days_left_display',)
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('system-report/',
                 self.admin_site.admin_view(system_report_view),
                 name='system_report'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['report_url'] = 'system-report/'
        return super().changelist_view(request, extra_context)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        try:
            profile = obj.user.profile
            profile.is_premium = obj.is_active and obj.ends_at >= date.today()
            profile.save(update_fields=['is_premium'])
        except Exception:
            pass

    def email_column(self, obj):
        try:
            return obj.user.email if obj.user else '—'
        except Exception:
            return '—'
    email_column.short_description = 'Email'

    def days_left_formatted(self, obj):
        try:
            days = _days_remaining(obj)
            if not obj.is_active:
                return mark_safe('<span style="color:#A32D2D">Revoked</span>')
            elif days > 7:
                return mark_safe(f'<span style="color:#3B6D11;font-weight:500">{days} days</span>')
            elif days > 0:
                return mark_safe(f'<span style="color:#854F0B;font-weight:500">{days} days</span>')
            else:
                return mark_safe('<span style="color:#888">Expired</span>')
        except Exception:
            return '—'
    days_left_formatted.short_description = 'Days left'

    def sub_status(self, obj):
        # NOTE: renamed from 'status_formatted' to avoid any Django field name conflicts
        try:
            days = _days_remaining(obj)
            if not obj.is_active:
                return mark_safe(
                    '<span style="background:#FCEBEB;color:#A32D2D;padding:3px 10px;'
                    'border-radius:12px;font-size:11px;font-weight:500">Revoked</span>'
                )
            if days > 7:
                return mark_safe(
                    '<span style="background:#EAF3DE;color:#3B6D11;padding:3px 10px;'
                    'border-radius:12px;font-size:11px;font-weight:500">Active</span>'
                )
            elif days > 0:
                return mark_safe(
                    '<span style="background:#FAEEDA;color:#854F0B;padding:3px 10px;'
                    'border-radius:12px;font-size:11px;font-weight:500">Expiring soon</span>'
                )
            else:
                return mark_safe(
                    '<span style="background:#f0f0f0;color:#888;padding:3px 10px;'
                    'border-radius:12px;font-size:11px;font-weight:500">Expired</span>'
                )
        except Exception:
            return '—'
    sub_status.short_description = 'Status'

    def sub_method(self, obj):
        # NOTE: renamed from 'payment_formatted' to avoid any conflicts
        try:
            if obj.payment:
                return mark_safe('<span style="color:#185FA5">Via payment</span>')
            return mark_safe('<span style="color:#888">Manual</span>')
        except Exception:
            return '—'
    sub_method.short_description = 'Method'

    def days_left_display(self, obj):
        try:
            return f"{_days_remaining(obj)} days"
        except Exception:
            return '—'
    days_left_display.short_description = 'Days remaining'

    def extend_30_days(self, request, queryset):
        extended = 0
        for sub in queryset:
            try:
                base = sub.ends_at if sub.ends_at >= date.today() else date.today()
                sub.ends_at   = base + timedelta(days=30)
                sub.is_active = True
                sub.save()
                try:
                    sub.user.profile.is_premium = True
                    sub.user.profile.save(update_fields=['is_premium'])
                except Exception:
                    pass
                extended += 1
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        self.message_user(request, f"Extended {extended} subscription(s) by 30 days")
    extend_30_days.short_description = "Extend by 30 days"

    def revoke_premium(self, request, queryset):
        revoked = 0
        for sub in queryset:
            try:
                sub.is_active = False
                sub.save()
                try:
                    sub.user.profile.is_premium = False
                    sub.user.profile.save(update_fields=['is_premium'])
                except Exception:
                    pass
                revoked += 1
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        self.message_user(request, f"Revoked premium for {revoked} user(s)")
    revoke_premium.short_description = "Revoke premium"

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="premium_users.csv"'
        writer = csv.writer(response)
        writer.writerow(['Username', 'Email', 'Start date', 'End date',
                         'Days left', 'Status', 'Method'])
        for sub in queryset:
            try:
                days   = _days_remaining(sub)
                status = "Active" if sub.is_active and days > 0 else "Inactive"
                writer.writerow([
                    sub.user.username if sub.user else "Unknown",
                    sub.user.email    if sub.user else "Unknown",
                    sub.started_at.strftime('%Y-%m-%d') if sub.started_at else "",
                    sub.ends_at.strftime('%Y-%m-%d')    if sub.ends_at    else "",
                    days,
                    status,
                    'Payment' if sub.payment else 'Manual'
                ])
            except Exception:
                continue
        return response
    export_to_csv.short_description = "Export to CSV"