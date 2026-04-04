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
        is_manual = report_data.get("is_manual", False)
        sync_type = "FORCED MANUAL OVERRIDE" if is_manual else "AUTONOMOUS NIGHTLY CYCLE"
        
        import zoneinfo
        tz = zoneinfo.ZoneInfo("America/New_York")
        now_str = datetime.now(tz).strftime("%Y-%m-%d %I:%M:%S %p %Z")
        
        subject = f"[ORACLE SYSTEM PULSE] - {sync_type} - {datetime.now(tz).strftime('%Y-%m-%d')}"
        
        # Build the dynamic HTML list for games
        game_rows = ""
        for game, data in report_data.get("sync_results", {}).items():
            if isinstance(data, dict):
                status = data.get("status", "UNKNOWN")
                completed_at = data.get("completed_at", "N/A")
                error_msg = data.get("error")
            else:
                # Legacy fallback
                status = data
                completed_at = "N/A"
                error_msg = None

            # JMc - [2026-04-04] - Robust accessibility: Use high-contrast green (#047857) for white backgrounds
            # and bright red (#dc2626) for errors.
            color = "#047857" if ("Added" in status or "Up to date" in status or "SUCCESS" in status) else "#dc2626"
            error_html = f'<br><span style="color:#dc2626; font-size:11px;"><strong>ERROR:</strong> {error_msg}</span>' if error_msg else ""
            
            game_rows += f'''
            <tr>
                <td style="padding:8px; border-bottom:1px solid #e2e8f0; color:#475569; vertical-align:top;">
                    <strong>{game}</strong><br>
                    <span style="font-size:11px; color:#94a3b8;">Completed: {completed_at}</span>
                </td>
                <td style="padding:8px; border-bottom:1px solid #e2e8f0; color:{color}; font-family:monospace; vertical-align:top; font-weight:bold;">
                    {status}
                    {error_html}
                </td>
            </tr>
            '''

        html_content = f"""
        <html>
            <body style="background-color: #f8fafc; color: #1e293b; font-family: sans-serif; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 30px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                    <h1 style="color: #0284c7; margin-top:0; border-bottom: 2px solid #0284c7; padding-bottom: 10px; font-size: 24px;">ORACLE SYSTEM PULSE</h1>
                    <div style="background-color: #f1f5f9; padding: 10px 15px; border-radius: 6px; margin-bottom: 20px;">
                        <p style="color: #475569; font-size: 13px; margin: 0;"><strong>PROTOCOL:</strong> {sync_type}</p>
                        <p style="color: #475569; font-size: 13px; margin: 5px 0 0 0;"><strong>TERMINATED:</strong> {now_str}</p>
                    </div>
                    
                    <h2 style="color: #1e293b; font-size: 16px; margin-top: 20px; text-transform: uppercase; letter-spacing: 1px;">01. Synchronization Status</h2>
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                        {game_rows}
                    </table>

                    <h2 style="color: #1e293b; font-size: 16px; margin-top: 20px; text-transform: uppercase; letter-spacing: 1px;">02. Syndicate Metrics</h2>
                    <p style="margin: 5px 0; color: #475569;">Total Technicians: <strong style="color:#0284c7;">{report_data.get('user_total', 0)}</strong></p>
                    <p style="margin: 5px 0; color: #475569;">Pro Tier Assets: <strong style="color:#0284c7;">{report_data.get('user_pro', 0)}</strong></p>
                    
                    <h2 style="color: #1e293b; font-size: 16px; margin-top: 20px; text-transform: uppercase; letter-spacing: 1px;">03. Database Vitality</h2>
                    <p style="font-size: 12px; color: #64748b; font-family: monospace;">Total Draw Records: {report_data.get('total_records', 0)}</p>
                    
                    <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                    <p style="font-size: 10px; color: #94a3b8; text-align: center; text-transform: uppercase; letter-spacing: 2px;">CONFIDENTIAL ADMINISTRATIVE TRANSMISSION // JMc Associates LLC</p>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(to_email, subject, html_content)

    @staticmethod
    def send_magic_link(email: str, token: str):
        """
        JMc - [2026-03-25] - Dispatches the passwordless authentication link.
        """
        frontend_url = os.getenv("FRONTEND_URL", "https://oracleapp.moderncyph3r.com")
        magic_link = f"{frontend_url}/verify?token={token}"
        subject = "[VAULT ACCESS] Your Oracle Authentication Link"
        
        # JMc - Branded HTML Template
        html = f"""
        <html>
            <body style="font-family: sans-serif; background-color: #020617; color: #f8fafc; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #0f172a; padding: 40px; border-radius: 12px; border: 1px solid #1e293b; text-align: center;">
                    <h2 style="color: #38bdf8; text-transform: uppercase; letter-spacing: 1px;">[ Authentication Required ]</h2>
                    <p style="font-size: 16px; line-height: 1.6; color: #cbd5e1; margin: 20px 0;">
                        Technician,<br><br>
                        A login request was initiated for your account. Click the button below to bypass the firewall and enter the Vault. This link is statistically significant and will expire in 15 minutes.
                    </p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{magic_link}" style="background-color: #3b82f6; color: #ffffff; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">AUTHENTICATE & ENTER</a>
                    </div>
                    <p style="font-size: 14px; color: #64748b;">
                        If you did not request this link, ignore this transmission. Your current matrices remain secure.
                    </p>
                    <hr style="border: 0; border-top: 1px solid #1e293b; margin: 30px 0;">
                    <p style="font-size: 10px; color: #475569;">
                        © 2026 JMc Associates, LLC. Oracle is a structural deployment tool.
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

        # JMc - [2026-03-31] - Added Plain Text fallback to kill spam filters.
        text_content = f"{subject}\n\nThis is an automated transmission from the Oracle. Please view in an HTML-capable client."
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        
        message.attach(part1)
        message.attach(part2)

        try:
            # JMc - [2026-03-18] - Port 465 requires SMTP_SSL (Implicit SSL)
            # Port 587 requires SMTP + starttls (Explicit SSL/TLS)
            if port == 465:
                server = smtplib.SMTP_SSL(host, port)
            else:
                server = smtplib.SMTP(host, port)
                server.starttls()
            
            server.login(user, password)
            server.sendmail(from_email, to_email, message.as_string())
            server.quit()
            
            logger.info(f"Oracle - Email Success - {subject} dispatched to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Oracle - Email Failure - Could not send to {to_email}: {e}")
            return False
