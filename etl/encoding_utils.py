"""Encoding detection utilities for CSV files."""
import chardet


def detect_encoding(file_path: str) -> str:
    """
    Detect the encoding of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Detected encoding name (e.g., 'utf-8', 'windows-1252')
    """
    with open(file_path, 'rb') as f:
        raw_data = f.read(100000)
    
    result = chardet.detect(raw_data)
    encoding = result.get('encoding', 'utf-8')
    
    if encoding and encoding.lower() in ['ascii', 'utf-8']:
        return 'utf-8'
    
    if encoding and encoding.lower() in ['windows-1252', 'cp1252', 'iso-8859-1', 'latin-1']:
        return 'windows-1252'
    
    return encoding or 'utf-8'
