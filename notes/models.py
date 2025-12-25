# notes/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import datetime

# Your existing Note model (if you have it)
class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    
    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    email_verified = models.BooleanField(default=False)
    verification_otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    
    def generate_otp(self):
        """Generate a 6-digit OTP"""
        self.verification_otp = str(random.randint(100000, 999999))
        self.otp_created_at = timezone.now()
        self.save()
        print(f"Generated OTP for {self.user.email}: {self.verification_otp}")
        return self.verification_otp
    
    def verify_otp(self, otp):
        """Check if OTP is valid and not expired (10 minutes)"""
        if self.verification_otp == otp:
            # Check if OTP is expired
            time_diff = timezone.now() - self.otp_created_at
            if time_diff < datetime.timedelta(minutes=10):
                self.email_verified = True
                self.verification_otp = None
                self.otp_created_at = None
                self.save()
                return True
        return False
    
    def __str__(self):
        return f"{self.user.username}"