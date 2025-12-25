# test_gmail.py - Run this FIRST
import smtplib
from email.mime.text import MIMEText

# Your Gmail credentials
gmail_user = 'sashankadada36@gmail.com'  # Your email
gmail_password = 'ijza lwtz xzoc zukg'     # Your password

def test_gmail_connection():
    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        
        # Login
        server.login(gmail_user, gmail_password)
        print("✅ Gmail login successful!")
        
        # Test sending
        msg = MIMEText("Test email from The Tuition Class")
        msg['Subject'] = 'Test Email'
        msg['From'] = gmail_user
        msg['To'] = gmail_user  # Send to yourself
        
        server.send_message(msg)
        print("✅ Test email sent successfully!")
        
        server.quit()
        return True
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        
        # Common error solutions
        if "Application-specific password" in str(e):
            print("\n🔧 SOLUTION: You need to:")
            print("1. Go to: https://myaccount.google.com/security")
            print("2. Enable '2-Step Verification'")
            print("3. Then create an 'App Password'")
            print("4. Use that 16-character password instead of your regular password")
        
        elif "Username and Password not accepted" in str(e):
            print("\n🔧 SOLUTION: Check your email and password")
            print("Make sure you're using the correct password")
            
        elif "Please log in via your web browser" in str(e):
            print("\n🔧 SOLUTION: Enable Less Secure Apps")
            print("Go to: https://myaccount.google.com/lesssecureapps")
            print("Turn ON 'Allow less secure apps'")
            
        return False

if __name__ == "__main__":
    test_gmail_connection()