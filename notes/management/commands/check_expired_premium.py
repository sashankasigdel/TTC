# notes/management/commands/check_expired_premium.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from notes.models import PremiumSubscription
from notes.email_utils import send_premium_expired_email

class Command(BaseCommand):
    help = 'Check for expired premium subscriptions and send emails'
    
    def handle(self, *args, **options):
        today = timezone.now().date()
        
        self.stdout.write(f"🔍 Checking for expired premium subscriptions on {today}")
        self.stdout.write("-" * 50)
        
        # Find subscriptions that expired TODAY and are still active
        expired_today = PremiumSubscription.objects.filter(
            is_active=True,
            ends_at=today
        )
        
        sent_count = 0
        
        for subscription in expired_today:
            self.stdout.write(f"📧 Sending expired email to: {subscription.user.email}")
            
            if send_premium_expired_email(subscription.user, subscription.ends_at):
                # Mark as inactive after successful email
                subscription.is_active = False
                subscription.save()
                
                # Update user profile
                if hasattr(subscription.user, 'profile'):
                    subscription.user.profile.update_premium_status()
                
                sent_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Email sent and subscription marked inactive")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"✗ Failed to send email")
                )
        
        # Check for any subscriptions that expired in the past but are still active
        # (in case the script wasn't run for a few days)
        past_expired = PremiumSubscription.objects.filter(
            is_active=True,
            ends_at__lt=today
        )
        
        past_count = 0
        
        for subscription in past_expired:
            self.stdout.write(f"🕒 Found past expired subscription for: {subscription.user.email}")
            
            if send_premium_expired_email(subscription.user, subscription.ends_at):
                subscription.is_active = False
                subscription.save()
                
                if hasattr(subscription.user, 'profile'):
                    subscription.user.profile.update_premium_status()
                
                past_count += 1
                self.stdout.write(
                    self.style.WARNING(f"✓ Late notification sent")
                )
        
        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("📊 SUMMARY")
        self.stdout.write("=" * 50)
        
        total_expired = expired_today.count() + past_expired.count()
        total_sent = sent_count + past_count
        
        if total_expired == 0:
            self.stdout.write(self.style.SUCCESS("✨ No expired subscriptions found today."))
        else:
            self.stdout.write(f"Found: {total_expired} expired subscription(s)")
            self.stdout.write(f"Sent: {total_sent} email(s)")
            
            if sent_count > 0:
                self.stdout.write(self.style.SUCCESS(f"✅ {sent_count} email(s) sent for today's expirations"))
            
            if past_count > 0:
                self.stdout.write(self.style.WARNING(f"🕒 {past_count} late notification(s) sent"))