import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

def send_reset_email(to_email: str, otp: str):
    subject = "Your Password Reset OTP"
    body = f"Your OTP to reset your password is : {otp}. It will expire in 10 minutes."

    msg=MIMEText(body)
    msg["Subject"]= subject
    msg["From"] = GMAIL_USER
    msg["TO"] = to_email

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, [to_email], msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")