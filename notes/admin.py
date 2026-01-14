# notes/admin.py - DYNAMIC VERSION
from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import redirect
from django.contrib import messages
from datetime import date, timedelta
from .models import UserProfile, Course, Subject, Chapter, Payment, PremiumSubscription

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
        color = 'green' if count > 0 else 'red'
        text = f"{count} subject{'s' if count != 1 else ''}"
        return format_html('<span style="color: {};">{}</span>', color, text)
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
        color = 'green' if count > 0 else 'red'
        text = f"{count} chapter{'s' if count != 1 else ''}"
        return format_html('<span style="color: {};">{}</span>', color, text)
    chapter_count_display.short_description = 'Chapters'

# ============================================================================
# 4. CHAPTER ADMIN (Dynamic Management)
# ============================================================================
@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'has_pdf', 'has_video', 'display_order', 'is_active', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('display_order', 'is_active')
    
    # Fields to show in add/edit form
    fieldsets = (
        ('Basic Information', {
            'fields': ('subject', 'title', 'slug', 'content')
        }),
         ('Chapter Resources', {
            'fields': ('pdf_file', 'video_url')
        }),
        ('Display Settings', {
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
# PAYMENT ADMIN
# ============================================================================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_display', 'submitted_at', 'screenshot_preview', 'approve_action']
    list_filter = ['submitted_at']
    search_fields = ['user__username', 'user__email', 'email']
    readonly_fields = ['submitted_at', 'screenshot_preview']
    
    def email_display(self, obj):
        return obj.email if hasattr(obj, 'email') and obj.email else "No email"
    email_display.short_description = 'Email'

    def screenshot_preview(self, obj):
        if obj.screenshot:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.screenshot.url)
        return "No screenshot"
    screenshot_preview.short_description = 'Screenshot'
    
    def approve_action(self, obj):
        """Show approve button if not already premium"""
        # Check if user already has active premium
        try:
            has_active = PremiumSubscription.objects.filter(
                user=obj.user,
                is_active=True,
                ends_at__gte=date.today()
            ).exists()
            
            if has_active:
                return format_html('<span class="text-success">✓ Already Premium</span>')
        except Exception as e:
            # If there's any error, assume not premium
            has_active = False
        
        return format_html(
            '<a href="/admin/notes/payment/{}/approve/" class="btn btn-success btn-sm">'
            '<i class="fas fa-check"></i> Approve'
            '</a>',
            obj.id
        )
    approve_action.short_description = 'Action'
    
    def make_premium(self, request, queryset):
        """Action to make users premium (creates PremiumSubscription)"""
        created = 0
        for payment in queryset:
            try:
                # Check if user already has a subscription
                existing_subs = PremiumSubscription.objects.filter(user=payment.user)
                
                if existing_subs.exists():
                    # Update the most recent subscription
                    existing_sub = existing_subs.first()
                    existing_sub.ends_at = date.today() + timedelta(days=30)
                    existing_sub.is_active = True
                    existing_sub.payment = payment
                    existing_sub.admin_notes = f'Updated from Payment #{payment.id}'
                    existing_sub.save()
                else:
                    # Create new subscription
                    PremiumSubscription.objects.create(
                        user=payment.user,
                        ends_at=date.today() + timedelta(days=30),
                        payment=payment,
                        admin_notes=f'Approved from Payment #{payment.id}',
                        is_active=True
                    )
                    created += 1
                    
            except Exception as e:
                messages.error(request, f"Error with payment {payment.id}: {str(e)}")
        
        self.message_user(request, f"✓ Created/updated premium for {created} users")
    make_premium.short_description = "✅ Make users premium"
    
    # Add approve/reject URLs
    def get_urls(self):
        from django.urls import path
        
        urls = super().get_urls()
        custom_urls = [
            path('<int:payment_id>/approve/', 
                 self.admin_site.admin_view(self.approve_payment),
                 name='payment_approve'),
        ]
        return custom_urls + urls
    
    def approve_payment(self, request, payment_id):
        """Approve payment and create premium subscription"""
        try:
            payment = Payment.objects.get(id=payment_id)
            
            # Check if user already has active premium
            has_active = PremiumSubscription.objects.filter(
                user=payment.user,
                is_active=True,
                ends_at__gte=date.today()
            ).exists()
            
            if has_active:
                messages.warning(
                    request, 
                    f"⚠ {payment.user.username} already has active premium."
                )
            else:
                # Create PremiumSubscription
                PremiumSubscription.objects.create(
                    user=payment.user,
                    ends_at=date.today() + timedelta(days=30),
                    payment=payment,
                    admin_notes=f"Approved payment #{payment.id}",
                    is_active=True
                )
                
                messages.success(
                    request, 
                    f"✓ Approved payment for {payment.user.username}. Premium active for 30 days."
                )
            
        except Payment.DoesNotExist:
            messages.error(request, "Payment not found")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        
        return redirect('/admin/notes/payment/')
    
    actions = [make_premium]


# Replace ONLY the PremiumSubscriptionAdmin class in your admin.py:

@admin.register(PremiumSubscription)
class PremiumSubscriptionAdmin(admin.ModelAdmin):
    """Simple admin for premium users section - Working version"""
    
    list_display = ['user', 'email_column', 'started_at', 'ends_at', 
                    'days_left_formatted', 'status_formatted', 'payment_formatted']
    list_filter = ['is_active', 'ends_at']
    search_fields = ['user__username', 'user__email', 'admin_notes']
    readonly_fields = ['started_at', 'days_left_display']
    list_per_page = 50
    actions = ['extend_30_days', 'revoke_premium', 'export_to_csv']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'payment', 'admin_notes')
        }),
        ('Subscription Dates', {
            'fields': ('started_at', 'ends_at', 'is_active')
        }),
        ('Status', {
            'fields': ('days_left_display',)
        }),
    )
    
    def email_column(self, obj):
        return obj.user.email if obj.user else "No user"
    email_column.short_description = 'Email'
    
    def days_left_formatted(self, obj):
        """Better formatted days remaining"""
        try:
            days = getattr(obj, 'days_remaining', 0)
            
            if not obj.is_active:
                return "🔴 Revoked"
            elif days > 7:
                return f"🟢 {days} days"
            elif days > 0:
                return f"🟡 {days} days"
            else:
                return "⚫ Expired"
        except:
            return "❓ Error"
    days_left_formatted.short_description = 'Days Left'
    
    def status_formatted(self, obj):
        """Better formatted status"""
        try:
            if not obj.is_active:
                return "🔴 Revoked"
            
            days = getattr(obj, 'days_remaining', 0)
            if days > 7:
                return "🟢 Active"
            elif days > 0:
                return "🟡 Expiring Soon"
            else:
                return "⚫ Expired"
        except:
            return "❓ Unknown"
    status_formatted.short_description = 'Status'
    
    def payment_formatted(self, obj):
        """Better formatted payment method"""
        if obj.payment:
            return "💳 Via Payment"
        return "👤 Manual"
    payment_formatted.short_description = 'Method'
    
    def days_left_display(self, obj):
        try:
            days = getattr(obj, 'days_remaining', 0)
            return f"{days} days"
        except:
            return "Error"
    days_left_display.short_description = 'Days Remaining'
    
    # Bulk actions (same as before)
    def extend_30_days(self, request, queryset):
        from datetime import date, timedelta
        
        extended = 0
        for subscription in queryset:
            try:
                if subscription.ends_at < date.today():
                    subscription.ends_at = date.today() + timedelta(days=30)
                else:
                    subscription.ends_at = subscription.ends_at + timedelta(days=30)
                subscription.is_active = True
                subscription.save()
                extended += 1
            except Exception as e:
                messages.error(request, f"Error extending subscription: {str(e)}")
        
        self.message_user(request, f"Extended {extended} subscription(s) by 30 days")
    extend_30_days.short_description = "Extend by 30 days"
    
    def revoke_premium(self, request, queryset):
        revoked = 0
        for subscription in queryset:
            try:
                subscription.is_active = False
                subscription.save()
                revoked += 1
            except Exception as e:
                messages.error(request, f"Error revoking subscription: {str(e)}")
        
        self.message_user(request, f"Revoked premium for {revoked} user(s)")
    revoke_premium.short_description = "Revoke premium"
    
    def export_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="premium_users.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Username', 'Email', 'Start Date', 'End Date', 
                        'Days Left', 'Status', 'Method'])
        
        for sub in queryset:
            try:
                days = getattr(sub, 'days_remaining', 0)
                status_text = "Active" if sub.is_active and days > 0 else "Inactive"
                writer.writerow([
                    sub.user.username if sub.user else "Unknown",
                    sub.user.email if sub.user else "Unknown",
                    sub.started_at.strftime('%Y-%m-%d') if sub.started_at else "Unknown",
                    sub.ends_at.strftime('%Y-%m-%d') if sub.ends_at else "Unknown",
                    days,
                    status_text,
                    'Payment' if sub.payment else 'Manual'
                ])
            except Exception as e:
                continue
        
        return response
    export_to_csv.short_description = "Export to CSV"