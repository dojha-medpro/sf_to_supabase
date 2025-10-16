"""Flask application for Salesforce to Supabase ETL Pipeline."""
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime, date
from pathlib import Path
import shutil

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
    load_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return load_id

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload and processing."""
    
    if 'csv_file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('index'))
    
    file = request.files['csv_file']
    mapping_name = request.form.get('mapping')
    partition_date_str = request.form.get('partition_date', datetime.now().strftime('%Y-%m-%d'))
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if not mapping_name:
        flash('No mapping selected', 'error')
        return redirect(url_for('index'))
    
    try:
        partition_date = datetime.strptime(partition_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid partition date format. Use YYYY-MM-DD', 'error')
        return redirect(url_for('index'))
    
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
        is_valid, errors, stats = validator.validate_file(str(upload_path))
        
        if not is_valid:
            quarantine_path = QUARANTINE_FOLDER / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            shutil.move(upload_path, quarantine_path)
            
            update_progress(load_id, 'Failed: QA validation errors', 100)
            error_report = '\n'.join(errors)
            notifier.notify_failure(filename, f"QA validation failed: {error_report}", str(quarantine_path))
            flash(f'❌ QA validation failed. File quarantined.\n\nErrors:\n{error_report}', 'error')
            return redirect(url_for('index'))
        
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
            mapping_name
        )
        
        upload_path.unlink(missing_ok=True)
        transformed_path.unlink(missing_ok=True)
        
        update_progress(load_id, 'Complete', 100)
        notifier.notify_success(filename, loaded_rows, target_table)
        flash(f'✅ Successfully loaded {loaded_rows} rows to {target_table}', 'success')
        flash(f'📊 Statistics: {stats["total_rows"]} rows processed', 'info')
        
    except Exception as e:
        quarantine_path = None
        if upload_path.exists():
            quarantine_path = QUARANTINE_FOLDER / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            shutil.move(upload_path, quarantine_path)
        
        notifier.notify_failure(filename, str(e), str(quarantine_path) if quarantine_path else None)
        flash(f'❌ Error processing file: {str(e)}', 'error')
        
        import traceback
        print(f"Error details:\n{traceback.format_exc()}")
    
    return redirect(url_for('index'))


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
