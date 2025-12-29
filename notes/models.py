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
    
    
# ============================================================================
# 2. COURSE MODEL (Dynamic - Add from admin)
# ============================================================================
class Course(models.Model):
    LEVEL_CHOICES = [
        ('+2', '+2 Level'),
        ('bachelor', 'Bachelor Level'),
        ('master', 'Master Level'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="URL-friendly version of title")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    description = models.TextField(blank=True, help_text="Course description shown on website")
    thumbnail = models.ImageField(
        upload_to='course_thumbnails/', 
        null=True, 
        blank=True,
        help_text="Optional course thumbnail image"
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Order in which courses appear (lower number = first)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide course from website"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'title']
    
    def __str__(self):
        return self.title
    
    def subject_count(self):
        """Count of active subjects in this course"""
        return self.subjects.filter(is_active=True).count()
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('course_detail', kwargs={'course_slug': self.slug})

# ============================================================================
# 3. SUBJECT MODEL (Dynamic - Add from admin)
# ============================================================================
class Subject(models.Model):
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='subjects',
        help_text="Select which course this subject belongs to"
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(help_text="URL-friendly version of title")
    description = models.TextField(blank=True, help_text="Subject description")
    display_order = models.IntegerField(
        default=0,
        help_text="Order in which subjects appear (lower number = first)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide subject from website"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'title']
        unique_together = ['course', 'slug']  # Same slug can't repeat in same course
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def chapter_count(self):
        """Count of active chapters in this subject"""
        return self.chapters.filter(is_active=True).count()
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('subject_detail', kwargs={
            'course_slug': self.course.slug,
            'subject_slug': self.slug
        })

# ============================================================================
# 4. CHAPTER MODEL (Dynamic - Add from admin)
# ============================================================================
class Chapter(models.Model):
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        related_name='chapters',
        help_text="Select which subject this chapter belongs to"
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(help_text="URL-friendly version of title")
    
    # Content field (for now - we'll add file uploads later)
    content = models.TextField(
        blank=True,
        help_text="Chapter content (text only for now)"
    )
    
    display_order = models.IntegerField(
        default=0,
        help_text="Order in which chapters appear (lower number = first)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide chapter from website"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'title']
        unique_together = ['subject', 'slug']  # Same slug can't repeat in same subject
    
    def __str__(self):
        return f"{self.subject.title} - {self.title}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('chapter_detail', kwargs={
            'course_slug': self.subject.course.slug,
            'subject_slug': self.subject.slug,
            'chapter_slug': self.slug
        })