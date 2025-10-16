import os
import markdown
from flask import Flask, render_template, send_from_directory, abort
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).parent

@app.route('/')
def index():
    """Homepage with navigation to all documentation sections."""
    return render_template('index.html')

@app.route('/schemas')
def schemas():
    """List all schemas."""
    schemas_dir = BASE_DIR / 'Schemas' / 'staging'
    objects = []
    if schemas_dir.exists():
        for obj_dir in sorted(schemas_dir.iterdir()):
            if obj_dir.is_dir():
                objects.append(obj_dir.name)
    return render_template('schemas.html', objects=objects)

@app.route('/schemas/<object_name>')
def schema_detail(object_name):
    """Display schema details for a specific object."""
    schema_dir = BASE_DIR / 'Schemas' / 'staging' / object_name
    if not schema_dir.exists():
        abort(404)
    
    files = {}
    for file in schema_dir.glob('*.md'):
        with open(file, 'r') as f:
            content = f.read()
            html_content = markdown.markdown(content, extensions=['tables', 'fenced_code'])
            files[file.stem.replace('_', ' ').title()] = html_content
    
    return render_template('schema_detail.html', object_name=object_name, files=files)

@app.route('/mappings')
def mappings():
    """List all mapping files."""
    mappings_dir = BASE_DIR / 'Mappings'
    mapping_files = []
    if mappings_dir.exists():
        for yaml_file in sorted(mappings_dir.glob('*.yaml')):
            mapping_files.append(yaml_file.stem)
    return render_template('mappings.html', mapping_files=mapping_files)

@app.route('/mappings/<mapping_name>')
def mapping_detail(mapping_name):
    """Display a specific mapping file."""
    mapping_file = BASE_DIR / 'Mappings' / f'{mapping_name}.yaml'
    if not mapping_file.exists():
        abort(404)
    
    with open(mapping_file, 'r') as f:
        content = f.read()
    
    return render_template('mapping_detail.html', mapping_name=mapping_name, content=content)

@app.route('/docs/<section>')
def docs(section):
    """Display documentation for Load Scripts, QA Scripts, Reports."""
    section_map = {
        'load-scripts': 'Load Scripts',
        'qa-scripts': 'QA scripts',
        'reports': 'Reports',
        'schemas': 'Schemas'
    }
    
    if section not in section_map:
        abort(404)
    
    readme_path = BASE_DIR / section_map[section] / 'README.md'
    if not readme_path.exists():
        abort(404)
    
    with open(readme_path, 'r') as f:
        content = f.read()
        html_content = markdown.markdown(content, extensions=['tables', 'fenced_code'])
    
    return render_template('docs.html', section=section_map[section], content=html_content)

@app.route('/release-notes')
def release_notes():
    """Display schema release notes."""
    notes_path = BASE_DIR / 'Schemas' / 'release_notes.md'
    if not notes_path.exists():
        return render_template('docs.html', section='Release Notes', content='<p>No release notes available.</p>')
    
    with open(notes_path, 'r') as f:
        content = f.read()
        html_content = markdown.markdown(content, extensions=['tables', 'fenced_code'])
    
    return render_template('docs.html', section='Release Notes', content=html_content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
