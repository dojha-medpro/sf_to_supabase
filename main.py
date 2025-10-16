"""Flask application for Salesforce to Supabase ETL Pipeline."""
import os
import base64
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime, date
from pathlib import Path
import shutil
import re
from urllib.parse import urlparse

from etl.mapper import MappingParser
from etl.transformer import CSVTransformer
from etl.validator import QAValidator
from etl.loader import BulkLoader
from etl.notifications import NotificationService

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

UPLOAD_FOLDER = Path('uploads')
QUARANTINE_FOLDER = Path('quarantine')
UPLOAD_FOLDER.mkdir(exist_ok=True)
QUARANTINE_FOLDER.mkdir(exist_ok=True)

mapper = MappingParser()
loader = BulkLoader()
notifier = NotificationService()


@app.route('/')
def index():
    """Homepage with upload form."""
    mappings = mapper.get_available_mappings()
    return render_template('index.html', mappings=mappings)


def update_progress(load_id: int, stage: str, progress: int):
    """Update progress for a load."""
    import psycopg2
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE load_history 
        SET current_stage = %s, progress_percent = %s
        WHERE id = %s
    """, (stage, progress, load_id))
    conn.commit()
    cursor.close()
    conn.close()

def update_progress_and_status(load_id: int, stage: str, progress: int, status: str):
    """Update progress and status for a load."""
    import psycopg2
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE load_history 
        SET current_stage = %s, progress_percent = %s, status = %s, completed_at = %s
        WHERE id = %s
    """, (stage, progress, status, datetime.now() if status in ('success', 'failed') else None, load_id))
    conn.commit()
    cursor.close()
    conn.close()

def create_load_record(filename: str, mapping_name: str, partition_date_str: str, target_table: str) -> int:
    """Create initial load record and return load_id."""
    import psycopg2
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO load_history 
        (load_date, target_table, file_name, mapping_file, status, current_stage, progress_percent, started_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (partition_date_str, target_table, filename, mapping_name, 'running', 'Starting upload', 0, datetime.now()))
    result = cursor.fetchone()
    if not result:
        raise RuntimeError("Failed to create load_history record")
    load_id = result[0]
    conn.commit()
    cursor.close()
    conn.close()
    return load_id

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload and processing."""
    
    if 'csv_file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    
    file = request.files['csv_file']
    mapping_name = request.form.get('mapping')
    partition_date_str = request.form.get('partition_date', datetime.now().strftime('%Y-%m-%d'))
    
    if not file.filename or file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not mapping_name:
        return jsonify({'success': False, 'error': 'No mapping selected'}), 400
    
    try:
        partition_date = datetime.strptime(partition_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid partition date format. Use YYYY-MM-DD'}), 400
    
    filename = secure_filename(file.filename)
    upload_path = UPLOAD_FOLDER / filename
    
    mapping = mapper.load_mapping(mapping_name)
    target_table = mapper.get_target_table(mapping)
    
    load_id = create_load_record(filename, mapping_name, partition_date_str, target_table)
    
    update_progress(load_id, 'Uploading file', 5)
    file.save(upload_path)
    
    try:
        source_report = mapping.get('source_report', 'Unknown')
        
        update_progress(load_id, 'Running QA validation', 10)
        validator = QAValidator(mapping)
        
        def validation_progress(percent, message):
            update_progress(load_id, message, percent)
        
        is_valid, errors, stats = validator.validate_file(str(upload_path), progress_callback=validation_progress)
        
        if not is_valid:
            quarantine_path = QUARANTINE_FOLDER / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            shutil.move(upload_path, quarantine_path)
            
            error_report = '\n'.join(errors)
            update_progress_and_status(load_id, 'Failed: QA validation errors', 100, 'failed')
            notifier.notify_failure(filename, f"QA validation failed: {error_report}", str(quarantine_path))
            
            return jsonify({
                'success': False,
                'load_id': load_id,
                'error': f'QA validation failed. File quarantined.\n\nErrors:\n{error_report}'
            }), 400
        
        update_progress(load_id, 'Transforming data', 30)
        transformer = CSVTransformer(mapping)
        transformed_path = UPLOAD_FOLDER / f"transformed_{filename}"
        
        row_count, transform_errors = transformer.transform_csv(
            str(upload_path),
            str(transformed_path),
            partition_date,
            filename,
            source_report
        )
        
        update_progress(load_id, 'Loading to Supabase', 50)
        
        if transform_errors:
            flash(f'⚠️ Transformation warnings: {len(transform_errors)} errors', 'warning')
        
        loaded_rows = loader.load_csv(
            str(transformed_path),
            target_table,
            partition_date_str,
            filename,
            mapping_name,
            load_id
        )
        
        upload_path.unlink(missing_ok=True)
        transformed_path.unlink(missing_ok=True)
        
        update_progress_and_status(load_id, 'Complete', 100, 'success')
        notifier.notify_success(filename, loaded_rows, target_table)
        
        return jsonify({
            'success': True,
            'load_id': load_id,
            'rows_loaded': loaded_rows,
            'message': f'Successfully loaded {loaded_rows} rows to {target_table}'
        })
        
    except Exception as e:
        quarantine_path = None
        if upload_path.exists():
            quarantine_path = QUARANTINE_FOLDER / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            shutil.move(upload_path, quarantine_path)
        
        update_progress_and_status(load_id, f'Failed: {str(e)[:50]}', 100, 'failed')
        notifier.notify_failure(filename, str(e), str(quarantine_path) if quarantine_path else None)
        
        import traceback
        print(f"Error details:\n{traceback.format_exc()}")
        
        return jsonify({
            'success': False,
            'load_id': load_id,
            'error': str(e)
        }), 500


@app.route('/history')
def history():
    """Show load history."""
    import psycopg2
    
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, load_date, target_table, file_name, mapping_file, 
                   rows_loaded, status, error_message, started_at, completed_at
            FROM load_history
            ORDER BY started_at DESC
            LIMIT 100
        """)
        
        loads = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('history.html', loads=loads)
        
    except Exception as e:
        flash(f'Error loading history: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/api/mappings')
def api_mappings():
    """API endpoint to get available mappings."""
    mappings = mapper.get_available_mappings()
    return jsonify(mappings)


@app.route('/api/progress/<int:load_id>')
def api_progress(load_id):
    """API endpoint to get progress for a specific load."""
    import psycopg2
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT status, current_stage, progress_percent, rows_loaded, error_message
            FROM load_history
            WHERE id = %s
        """, (load_id,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return jsonify({
                'status': result[0],
                'stage': result[1] or 'Processing',
                'progress': result[2] or 0,
                'rows_loaded': result[3],
                'error_message': result[4]
            })
        else:
            return jsonify({'error': 'Load not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def auto_detect_mapping(filename: str):
    """Auto-detect YAML mapping based on CSV filename patterns.
    
    Returns:
        str or None: Mapping filename if pattern matched, None otherwise
    """
    filename_lower = filename.lower()
    
    mapping_patterns = {
        'contact': 'contacts.yaml',
        'candidate': 'contacts.yaml',
        'form_submission': 'form_submission.yaml',
        'job_applicant_history': 'job_applicant_history_events.yaml',
        'job_applicant': 'job_applicants.yaml',
        'applicant': 'job_applicants.yaml',
        'contacts_with_jobs': 'contacts_with_jobs_joined.yaml',
        'jobs_and_placement': 'jobs_and_placement.yaml',
        'placement_history': 'placement_history_events.yaml',
    }
    
    for pattern, mapping_file in mapping_patterns.items():
        if pattern in filename_lower:
            return mapping_file
    
    return None


def download_attachment(attachment: dict) -> tuple:
    """Download attachment from CloudMailin (base64 or URL).
    
    Security:
        - URLs are validated against allowed cloud storage domains
        - Timeout enforced to prevent hanging requests
        - Size limit enforced before download
    """
    filename = secure_filename(attachment.get('file_name', 'unknown.csv'))
    
    if 'content' in attachment:
        content = base64.b64decode(attachment['content'])
    elif 'url' in attachment:
        url = attachment['url']
        
        # Security: Parse URL and validate hostname against allowed cloud storage domains
        try:
            parsed = urlparse(url)
        except Exception:
            raise ValueError(f"Invalid attachment URL: {url}")
        
        if parsed.scheme != 'https':
            raise ValueError(f"Attachment URL must use HTTPS: {url}")
        
        hostname = parsed.hostname
        if not hostname:
            raise ValueError(f"Attachment URL has no hostname: {url}")
        
        # Strict domain validation - hostname must exactly match or end with allowed domain
        allowed_domains = [
            's3.amazonaws.com',
            'storage.googleapis.com',
            'blob.core.windows.net',
            'cloudmailin.com',
            'digitaloceanspaces.com',
            'r2.cloudflarestorage.com'
        ]
        
        is_allowed = False
        for domain in allowed_domains:
            if hostname == domain or hostname.endswith('.' + domain):
                is_allowed = True
                break
        
        if not is_allowed:
            raise ValueError(f"Attachment URL from untrusted domain: {hostname}")
        
        # Security: Download with timeout and size limit
        max_size = 100 * 1024 * 1024  # 100 MB
        
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        # Check size before downloading
        content_length = response.headers.get('Content-Length')
        if content_length and int(content_length) > max_size:
            raise ValueError(f"Attachment too large: {content_length} bytes (max {max_size})")
        
        # Download content with size check
        content = b''
        for chunk in response.iter_content(chunk_size=8192):
            content += chunk
            if len(content) > max_size:
                raise ValueError(f"Attachment exceeded size limit during download")
        
    else:
        raise ValueError("Attachment has neither 'content' nor 'url'")
    
    upload_path = UPLOAD_FOLDER / filename
    upload_path.write_bytes(content)
    
    return filename, upload_path


def process_csv_attachment(filename: str, upload_path: Path, mapping_name: str, partition_date: date):
    """Process CSV file through ETL pipeline (shared logic)."""
    mapping = mapper.load_mapping(mapping_name)
    target_table = mapper.get_target_table(mapping)
    
    load_id = create_load_record(filename, mapping_name, partition_date.strftime('%Y-%m-%d'), target_table)
    
    try:
        source_report = mapping.get('source_report', 'Unknown')
        
        update_progress(load_id, 'Running QA validation', 10)
        validator = QAValidator(mapping)
        
        def validation_progress(percent, message):
            update_progress(load_id, message, percent)
        
        is_valid, errors, stats = validator.validate_file(str(upload_path), progress_callback=validation_progress)
        
        if not is_valid:
            quarantine_path = QUARANTINE_FOLDER / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            shutil.move(upload_path, quarantine_path)
            
            error_report = '\n'.join(errors)
            update_progress_and_status(load_id, 'Failed: QA validation errors', 100, 'failed')
            notifier.notify_failure(filename, f"QA validation failed: {error_report}", str(quarantine_path))
            raise ValueError(f'QA validation failed: {error_report}')
        
        update_progress(load_id, 'Transforming data', 30)
        transformer = CSVTransformer(mapping)
        transformed_path = UPLOAD_FOLDER / f"transformed_{filename}"
        
        row_count, transform_errors = transformer.transform_csv(
            str(upload_path),
            str(transformed_path),
            partition_date,
            filename,
            source_report
        )
        
        update_progress(load_id, 'Loading to Supabase', 50)
        
        loaded_rows = loader.load_csv(
            str(transformed_path),
            target_table,
            partition_date.strftime('%Y-%m-%d'),
            filename,
            mapping_name,
            load_id
        )
        
        upload_path.unlink(missing_ok=True)
        transformed_path.unlink(missing_ok=True)
        
        update_progress_and_status(load_id, 'Complete', 100, 'success')
        notifier.notify_success(filename, loaded_rows, target_table)
        
        return load_id, loaded_rows, target_table
        
    except Exception as e:
        quarantine_path = None
        if upload_path.exists():
            quarantine_path = QUARANTINE_FOLDER / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            shutil.move(upload_path, quarantine_path)
        
        update_progress_and_status(load_id, f'Failed: {str(e)[:50]}', 100, 'failed')
        notifier.notify_failure(filename, str(e), str(quarantine_path) if quarantine_path else None)
        raise


@app.route('/webhook/cloudmailin', methods=['POST'])
def cloudmailin_webhook():
    """Receive emails from CloudMailin with CSV attachments.
    
    Security:
        - Uses HTTP Basic Authentication (CloudMailin recommended approach)
        - Validates credentials against CLOUDMAILIN_USERNAME and CLOUDMAILIN_PASSWORD
        - Configure CloudMailin URL as: https://username:password@your-domain/webhook/cloudmailin
    """
    # Security: Verify HTTP Basic Auth credentials (FAIL CLOSED)
    auth_username = os.environ.get('CLOUDMAILIN_USERNAME', 'cloudmailin')
    # Use existing CLOUDMAILIN_WEBHOOK_TOKEN as password for backward compatibility
    auth_password = os.environ.get('CLOUDMAILIN_PASSWORD') or os.environ.get('CLOUDMAILIN_WEBHOOK_TOKEN')
    
    if not auth_password:
        app.logger.error("CLOUDMAILIN_PASSWORD or CLOUDMAILIN_WEBHOOK_TOKEN not configured - rejecting request")
        return jsonify({'status': 'error', 'message': 'Webhook not configured'}), 500
    
    # Parse Authorization header
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Basic '):
        app.logger.warning(f"Missing Basic Auth from {request.remote_addr}")
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    try:
        import base64
        # Decode base64 credentials
        encoded_credentials = auth_header[6:]  # Remove "Basic " prefix
        decoded = base64.b64decode(encoded_credentials).decode('utf-8')
        provided_username, provided_password = decoded.split(':', 1)
        
        # Validate credentials
        if provided_username != auth_username or provided_password != auth_password:
            app.logger.warning(f"Invalid credentials from {request.remote_addr}")
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
            
    except Exception as e:
        app.logger.warning(f"Auth parsing error from {request.remote_addr}: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'No JSON payload received'}), 400
        
        envelope = data.get('envelope', {})
        headers = data.get('headers', {})
        attachments = data.get('attachments', [])
        
        from_email = envelope.get('from', 'unknown')
        subject = headers.get('subject', 'No Subject')
        
        app.logger.info(f"Received email from {from_email} with subject: {subject}")
        
        if not attachments:
            return jsonify({'status': 'error', 'message': 'No attachments found in email'}), 400
        
        results = []
        partition_date = date.today()
        
        for attachment in attachments:
            file_name = attachment.get('file_name', '')
            
            if not file_name.lower().endswith('.csv'):
                app.logger.info(f"Skipping non-CSV attachment: {file_name}")
                continue
            
            mapping_name = auto_detect_mapping(file_name)
            
            if not mapping_name:
                app.logger.warning(f"Could not auto-detect mapping for: {file_name}")
                results.append({
                    'file': file_name,
                    'status': 'skipped',
                    'reason': 'No matching mapping pattern'
                })
                continue
            
            try:
                filename, upload_path = download_attachment(attachment)
                
                load_id, loaded_rows, target_table = process_csv_attachment(
                    filename, upload_path, mapping_name, partition_date
                )
                
                results.append({
                    'file': file_name,
                    'status': 'success',
                    'load_id': load_id,
                    'rows_loaded': loaded_rows,
                    'target_table': target_table
                })
                
            except Exception as e:
                app.logger.error(f"Error processing {file_name}: {str(e)}")
                results.append({
                    'file': file_name,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return jsonify({
            'status': 'ok',
            'email_from': from_email,
            'email_subject': subject,
            'processed_files': results
        }), 200
        
    except Exception as e:
        app.logger.error(f"Webhook error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
