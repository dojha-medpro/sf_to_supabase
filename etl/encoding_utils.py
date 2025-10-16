"""Encoding detection utilities for CSV files."""
import chardet


def detect_encoding(file_path: str) -> tuple[str, str]:
    """
    Detect the encoding of a file with fallback handling.
    OPTIMIZED: Only reads first 100KB for detection instead of entire file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Tuple of (encoding, errors_mode) where errors_mode is 'strict', 'replace', or 'ignore'
    """
    encodings_to_try = ['utf-8', 'windows-1252', 'iso-8859-1', 'latin-1', 'cp1252']
    
    # Read only first 100KB for encoding detection (much faster for large files)
    with open(file_path, 'rb') as f:
        raw_data = f.read(100 * 1024)  # 100KB sample
    
    result = chardet.detect(raw_data)
    detected = result.get('encoding', '')
    confidence = result.get('confidence', 0)
    
    if detected and confidence > 0.7:
        detected_lower = detected.lower()
        
        if detected_lower in ['ascii']:
            return 'utf-8', 'strict'
        
        if detected_lower in ['windows-1252', 'cp1252']:
            return 'windows-1252', 'strict'
        
        if detected_lower in ['iso-8859-1', 'latin-1', 'latin1']:
            return 'iso-8859-1', 'strict'
        
        if detected_lower in ['utf-8', 'utf8']:
            try:
                raw_data.decode('utf-8')
                return 'utf-8', 'strict'
            except UnicodeDecodeError:
                return 'utf-8', 'replace'
    
    # Fallback: try common encodings on the sample
    for encoding in encodings_to_try:
        try:
            raw_data.decode(encoding)
            return encoding, 'strict'
        except (UnicodeDecodeError, LookupError):
            continue
    
    return 'utf-8', 'replace'
