"""QA Validation Framework - Validates CSV data quality."""
import csv
from typing import Dict, List, Any, Tuple
from collections import Counter
from .encoding_utils import detect_encoding


class QAValidator:
    """Validates CSV data quality before loading."""
    
    def __init__(self, mapping: Dict[str, Any]):
        self.mapping = mapping
        self.column_mapping = mapping.get('columns', {})
        self.natural_key = mapping.get('natural_key', [])
        self.reject_rules = mapping.get('reject_rules', [])
    
    def validate_file(self, csv_file: str, progress_callback=None) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validate a CSV file in a SINGLE pass for performance.
        
        Args:
            csv_file: Path to CSV file
            progress_callback: Optional function to call with progress updates (percent, message)
        
        Returns:
            (is_valid, errors, stats) tuple
        """
        errors = []
        stats = {
            'total_rows': 0,
            'duplicates': 0,
            'missing_keys': 0,
            'type_errors': 0
        }
        
        encoding, errors_mode = detect_encoding(csv_file)
        
        keys_seen = []
        missing_key_errors = []
        
        with open(csv_file, 'r', encoding=encoding, errors=errors_mode) as f:
            reader = csv.DictReader(f)
            
            # Validate headers first
            if not reader.fieldnames:
                errors.append("CSV file has no headers")
                return False, errors, stats
            
            source_headers = set(reader.fieldnames)
            expected_headers = set(self.column_mapping.keys())
            
            missing_headers = expected_headers - source_headers
            extra_headers = source_headers - expected_headers
            
            if missing_headers:
                errors.append(f"Missing expected headers: {', '.join(sorted(missing_headers))}")
            
            if extra_headers:
                errors.append(f"Extra headers not in mapping: {', '.join(sorted(extra_headers))}")
            
            # Single pass: count rows, check duplicates, validate required fields
            for row_num, row in enumerate(reader, start=2):
                stats['total_rows'] += 1
                
                # Report progress every 50,000 rows for large files
                if progress_callback and stats['total_rows'] % 50000 == 0:
                    progress_percent = min(10 + int((stats['total_rows'] / 500000) * 15), 25)
                    progress_callback(progress_percent, f'Validating row {stats["total_rows"]:,}...')
                
                # Check for duplicate keys
                if self.natural_key:
                    key_values = tuple(row.get(col, '') for col in self.natural_key)
                    keys_seen.append(key_values)
                    
                    # Check for missing required fields
                    for key_col in self.natural_key:
                        value = row.get(key_col, '').strip()
                        
                        if not value or value in ('', 'NULL', 'N/A', 'null'):
                            stats['missing_keys'] += 1
                            if len(missing_key_errors) < 10:
                                missing_key_errors.append(f"Row {row_num}: Missing required field '{key_col}'")
        
        # Process duplicate keys
        if self.natural_key and keys_seen:
            key_counts = Counter(keys_seen)
            duplicates = {k: count for k, count in key_counts.items() if count > 1}
            stats['duplicates'] = len(duplicates)
            
            if duplicates:
                for key, count in list(duplicates.items())[:5]:
                    errors.append(f"Duplicate key {dict(zip(self.natural_key, key))}: {count} occurrences")
                
                if len(duplicates) > 5:
                    errors.append(f"... and {len(duplicates) - 5} more duplicate keys")
        
        # Add missing key errors
        errors.extend(missing_key_errors)
        if stats['missing_keys'] > 10:
            errors.append(f"... and {stats['missing_keys'] - 10} more rows with missing keys")
        
        is_valid = len(errors) == 0
        
        return is_valid, errors, stats
