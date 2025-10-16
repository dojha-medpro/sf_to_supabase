"""Encoding detection utilities for CSV files."""
import chardet


def detect_encoding(file_path: str) -> str:
    """
    Detect the encoding of a file with fallback handling.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Detected encoding name (e.g., 'utf-8', 'windows-1252', 'latin-1')
    """
    encodings_to_try = ['utf-8', 'windows-1252', 'iso-8859-1', 'latin-1', 'cp1252']
    
    with open(file_path, 'rb') as f:
        raw_data = f.read(100000)
    
    result = chardet.detect(raw_data)
    detected = result.get('encoding', '')
    confidence = result.get('confidence', 0)
    
    if detected and confidence > 0.7:
        detected_lower = detected.lower()
        
        if detected_lower in ['ascii']:
            return 'utf-8'
        
        if detected_lower in ['windows-1252', 'cp1252']:
            return 'windows-1252'
        
        if detected_lower in ['iso-8859-1', 'latin-1', 'latin1']:
            return 'iso-8859-1'
        
        if detected_lower in ['utf-8', 'utf8']:
            try:
                raw_data.decode('utf-8')
                return 'utf-8'
            except UnicodeDecodeError:
                pass
    
    for encoding in encodings_to_try:
        try:
            raw_data.decode(encoding)
            return encoding
        except (UnicodeDecodeError, LookupError):
            continue
    
    return 'utf-8'
