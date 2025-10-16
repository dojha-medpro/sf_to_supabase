"""Notification system for ETL pipeline failures."""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationService:
    """Handles notifications for ETL pipeline events."""
    
    def __init__(self, log_file: str = "etl_notifications.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(exist_ok=True)
    
    def notify_failure(self, file_name: str, error_message: str, 
                      quarantine_path: Optional[str] = None):
        """
        Log and notify about ETL failure.
        
        In production, this can be extended to send emails via SMTP.
        For now, logs to file and console.
        """
        notification = {
            'timestamp': datetime.now().isoformat(),
            'type': 'FAILURE',
            'file_name': file_name,
            'error': error_message,
            'quarantine_path': quarantine_path
        }
        
        self._log_notification(notification)
        logger.error(f"ETL Failure: {file_name} - {error_message}")
    
    def notify_success(self, file_name: str, rows_loaded: int, target_table: str):
        """Log successful load."""
        notification = {
            'timestamp': datetime.now().isoformat(),
            'type': 'SUCCESS',
            'file_name': file_name,
            'rows_loaded': rows_loaded,
            'target_table': target_table
        }
        
        self._log_notification(notification)
        logger.info(f"ETL Success: {file_name} - {rows_loaded} rows to {target_table}")
    
    def _log_notification(self, notification: dict):
        """Write notification to log file."""
        with open(self.log_file, 'a') as f:
            f.write(f"{notification}\n")
    
    def send_email_notification(self, recipient: str, subject: str, body: str):
        """
        Placeholder for email notifications.
        
        To enable email notifications:
        1. Set SMTP environment variables:
           - SMTP_HOST
           - SMTP_PORT
           - SMTP_USER
           - SMTP_PASSWORD
        
        2. Or use a service like SendGrid/Mailgun with API key
        """
        logger.warning(
            f"Email notification not configured. "
            f"Would send to {recipient}: {subject}"
        )
