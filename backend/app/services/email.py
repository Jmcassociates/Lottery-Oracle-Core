import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailService:
    """
    JMc - [2026-03-18] - High-velocity transactional email service. 
    Handles Magic Link dispatch and Syndicate notifications.
    """
    
    @staticmethod
    def send_admin_report(to_email: str, report_data: dict):
        """
        JMc - [2026-03-18] - Dispatches the daily 'Executive Briefing' to the lead architect.
        Contains database stats, sync status, and system alerts.
        """
        subject = f"[ORACLE SYSTEM PULSE] - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Build the dynamic HTML list for games
        game_rows = ""
        for game, status in report_data.get("sync_results", {}).items():
            color = "#10b981" if "Added" in status or "Up to date" in status else "#ef4444"
            game_rows += f"<tr><td style='padding:8px; border-bottom:1px solid #1e293b; color:#94a3b8;'>{game}</td><td style='padding:8px; border-bottom:1px solid #1e293b; color:{color}; font-family:monospace;'>{status}</td></tr>"

        html_content = f"""
        <html>
            <body style="background-color: #020617; color: #cbd5e1; font-family: sans-serif; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 30px;">
                    <h1 style="color: #ffffff; margin-top:0; border-bottom: 2px solid #38bdf8; padding-bottom: 10px;">SYSTEM PULSE</h1>
                    
                    <h2 style="color: #38bdf8; font-size: 14px; text-transform: uppercase;">01. Synchronization Status</h2>
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                        {game_rows}
                    </table>

                    <h2 style="color: #38bdf8; font-size: 14px; text-transform: uppercase;">02. Syndicate Metrics</h2>
                    <p style="margin: 5px 0;">Total Technicians: <strong style="color:#ffffff;">{report_data.get('user_total', 0)}</strong></p>
                    <p style="margin: 5px 0;">Pro Tier Assets: <strong style="color:#10b981;">{report_data.get('user_pro', 0)}</strong></p>
                    
                    <h2 style="color: #38bdf8; font-size: 14px; text-transform: uppercase;">03. Database Vitality</h2>
                    <p style="font-size: 12px; color: #94a3b8; font-family: monospace;">Total Draw Records: {report_data.get('total_records', 0)}</p>
                    
                    <hr style="border: 0; border-top: 1px solid #1e293b; margin: 30px 0;">
                    <p style="font-size: 10px; color: #475569; text-align: center;">CONFIDENTIAL ADMINISTRATIVE TRANSMISSION // JMc Associates LLC</p>
                </div>
            </body>
        </html>
        """
        return EmailService._send_email(to_email, subject, html_content)
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
            # JMc - [2026-03-18] - Port 465 requires SMTP_SSL (Implicit SSL)
            # Port 587 requires SMTP + starttls (Explicit SSL/TLS)
            if port == 465:
                server = smtplib.SMTP_SSL(host, port)
            else:
                server = smtplib.SMTP(host, port)
                server.starttls()
            
            with server:
                server.login(user, password)
                server.sendmail(from_email, to_email, message.as_string())
            
            logger.info(f"Oracle - Email Success - Magic link dispatched to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Oracle - Email Failure - Could not send to {to_email}: {e}")
            return False
