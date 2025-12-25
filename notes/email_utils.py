# notes/email_utils.py - REAL EMAIL ONLY
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_otp_email(email, otp):
    """Send REAL OTP email - NO CONSOLE FALLBACK"""
    
    subject = "🔐 Verify Your Email - The Tuition Class"
    
    # Professional HTML email
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Verification</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
                background-color: #f5f7fa;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .otp-container {{
                background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
                border-radius: 12px;
                padding: 30px;
                text-align: center;
                margin: 30px 0;
                border: 2px solid #e2e8f0;
            }}
            .otp-code {{
                font-size: 48px;
                font-weight: bold;
                color: #2d3748;
                letter-spacing: 15px;
                font-family: 'Courier New', monospace;
                margin: 20px 0;
                padding: 15px;
                background: white;
                border-radius: 8px;
                display: inline-block;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .warning-box {{
                background: #fff5f5;
                border: 2px solid #fed7d7;
                border-radius: 8px;
                padding: 20px;
                margin: 30px 0;
            }}
            .footer {{
                background: #f7fafc;
                padding: 25px 30px;
                text-align: center;
                border-top: 1px solid #e2e8f0;
                color: #718096;
                font-size: 14px;
            }}
            .button {{
                display: inline-block;
                background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
                color: white;
                padding: 14px 30px;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 16px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header -->
            <div class="header">
                <h1>
                    <span>📚</span>
                    The Tuition Class
                </h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 18px;">
                    Complete Your Registration
                </p>
            </div>
            
            <!-- Content -->
            <div class="content">
                <h2 style="color: #2d3748; margin-top: 0;">Hello Future Learner! 👋</h2>
                
                <p style="font-size: 16px; line-height: 1.7;">
                    Welcome to <strong>The Tuition Class</strong> - your trusted online learning platform! 
                    We're excited to have you join our community of students.
                </p>
                
                <p style="font-size: 16px;">
                    To activate your account and access all study materials, please verify your email address using the code below:
                </p>
                
                <!-- OTP Box -->
                <div class="otp-container">
                    <p style="margin: 0 0 15px 0; color: #4a5568; font-size: 16px;">
                        Your 6-digit verification code:
                    </p>
                    <div class="otp-code">{otp}</div>
                    <p style="margin: 15px 0 0 0; color: #718096;">
                        ⏰ Valid for <strong>10 minutes</strong>
                    </p>
                </div>
                
                <p style="text-align: center; margin: 25px 0;">
                    <a href="http://127.0.0.1:8000/verify-email/" class="button">
                        Go to Verification Page →
                    </a>
                </p>
                
                <!-- Warning -->
                <div class="warning-box">
                    <h3 style="color: #c53030; margin-top: 0;">
                        ⚠️ Security Notice
                    </h3>
                    <p style="margin: 0; color: #742a2a;">
                        • This code is for your use only<br>
                        • Never share it with anyone<br>
                        • Our team will never ask for this code<br>
                        • If you didn't request this, please ignore this email
                    </p>
                </div>
                
                <p style="font-size: 15px; color: #4a5568;">
                    Having trouble? Simply enter the code above on our verification page, or reply to this email for assistance.
                </p>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <p style="margin: 0 0 10px 0;">
                    <strong>The Tuition Class</strong><br>
                    Pokhara, Nepal
                </p>
                <p style="margin: 5px 0; font-size: 13px;">
                    📧 thetuitionclass01@gmail.com<br>
                    📞 +977 9745289791
                </p>
                <p style="margin: 15px 0 0 0; font-size: 12px; color: #a0aec0;">
                    © 2025 The Tuition Class. Empowering education through technology.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version for email clients
    plain_text = f"""
    THE TUITION CLASS - EMAIL VERIFICATION
    
    Welcome to The Tuition Class!
    
    Your verification code is: {otp}
    
    Enter this 6-digit code on our verification page to activate your account.
    
    Verification page: http://127.0.0.1:8000/verify-email/
    
    This code is valid for 10 minutes.
    
    SECURITY NOTICE:
    - This code is for your use only
    - Never share it with anyone
    - Our team will never ask for this code
    - If you didn't request this, please ignore this email
    
    Need help? Reply to this email or contact:
    Email: thetuitionclass01@gmail.com
    Phone: +977 9745289791
    
    © 2025 The Tuition Class
    Pokhara, Nepal
    """
    
    try:
        # Create email
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
            reply_to=['thetuitionclass01@gmail.com'],
            headers={
                'X-Priority': '1',
                'Importance': 'High',
            }
        )
        
        # Attach HTML version
        email_msg.attach_alternative(html_content, "text/html")
        
        # Send it - NO FALLBACK
        email_msg.send(fail_silently=False)
        
        print(f"✅ REAL EMAIL SENT to: {email}")
        print(f"📨 From: {settings.DEFAULT_FROM_EMAIL}")
        print(f"🔐 OTP: {otp}")
        
        return True
        
    except Exception as e:
        print(f"❌ EMAIL FAILED for {email}")
        print(f"Error: {str(e)}")
        
        # NO CONSOLE FALLBACK - Let it fail
        raise Exception(f"Failed to send email: {str(e)}")