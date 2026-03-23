import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class EmailService:
    """
    JMc - [2026-03-18] - High-velocity transactional email service. 
    Handles Magic Link dispatch and Syndicate notifications.
    """
    
    @staticmethod
    def send_magic_link(email: str, magic_link: str):
        """
        Sends a secure Magic Link to the user.
        """
        subject = "Welcome to the Syndicate - Your Oracle Access Link"
        
        # JMc - Branded HTML Template
        html = f"""
        <html>
            <body style="font-family: sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #1e293b; padding: 40px; border-radius: 12px; border: 1px solid #334155;">
                    <h2 style="color: #38bdf8; text-align: center; font-size: 24px; margin-bottom: 20px;">The Oracle has spoken.</h2>
                    <p style="font-size: 16px; line-height: 1.6; color: #cbd5e1;">
                        Your access credentials for the Lottery Oracle dashboard have been forged. 
                        Click the button below to enter the Vault. This link is statistically significant and will expire in 15 minutes.
                    </p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{magic_link}" style="background-color: #38bdf8; color: #0f172a; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 16px;">Access the Vault</a>
                    </div>
                    <p style="font-size: 14px; color: #64748b; text-align: center;">
                        If you did not request this link, ignore this transmission. Your current matrices remain secure.
                    </p>
                    <hr style="border: 0; border-top: 1px solid #334155; margin: 30px 0;">
                    <p style="font-size: 12px; color: #475569; text-align: center;">
                        © 2026 JMc Associates LLC. Oracle is a structural deployment tool.
                    </p>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(email, subject, html)

    @staticmethod
    def _send_email(to_email: str, subject: str, html_content: str):
        host = os.getenv("SMTP_HOST")
        port = int(os.getenv("SMTP_PORT", 587))
        user = os.getenv("SMTP_USER")
        password = os.getenv("SMTP_PASSWORD")
        from_email = os.getenv("SMTP_FROM_EMAIL")
        from_name = os.getenv("SMTP_FROM_NAME", "Lottery Oracle")

        if not all([host, user, password, from_email]):
            logger.error("Oracle - Email Error - Missing SMTP configuration.")
            return False

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{from_name} <{from_email}>"
        message["To"] = to_email

        part = MIMEText(html_content, "html")
        message.attach(part)

        try:
            with smtplib.SMTP(host, port) as server:
                server.starttls()
                server.login(user, password)
                server.sendmail(from_email, to_email, message.as_string())
            logger.info(f"Oracle - Email Success - Magic link dispatched to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Oracle - Email Failure - Could not send to {to_email}: {e}")
            return False
