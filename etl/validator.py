"""QA Validation Framework - Validates CSV data quality."""
import csv
from typing import Dict, List, Any, Tuple
from collections import Counter


class QAValidator:
    """Validates CSV data quality before loading."""
    
    def __init__(self, mapping: Dict[str, Any]):
        self.mapping = mapping
        self.column_mapping = mapping.get('columns', {})
        self.natural_key = mapping.get('natural_key', [])
        self.reject_rules = mapping.get('reject_rules', [])
    
    def validate_file(self, csv_file: str) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validate a CSV file.
        
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
        
        errors.extend(self._validate_headers(csv_file))
        
        duplicate_errors, dup_count = self._validate_duplicates(csv_file)
        errors.extend(duplicate_errors)
        stats['duplicates'] = dup_count
        
        key_errors, missing_count = self._validate_required_fields(csv_file)
        errors.extend(key_errors)
        stats['missing_keys'] = missing_count
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            stats['total_rows'] = sum(1 for _ in reader)
        
        is_valid = len(errors) == 0
        
        return is_valid, errors, stats
    
    def _validate_headers(self, csv_file: str) -> List[str]:
        """Validate CSV headers match mapping."""
        errors = []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            if not reader.fieldnames:
                return ["CSV file has no headers"]
            
            source_headers = set(reader.fieldnames)
            expected_headers = set(self.column_mapping.keys())
            
            missing_headers = expected_headers - source_headers
            extra_headers = source_headers - expected_headers
            
            if missing_headers:
                errors.append(f"Missing expected headers: {', '.join(sorted(missing_headers))}")
            
            if extra_headers:
                errors.append(f"Extra headers not in mapping: {', '.join(sorted(extra_headers))}")
        
        return errors
    
    def _validate_duplicates(self, csv_file: str) -> Tuple[List[str], int]:
        """Check for duplicate keys."""
        errors = []
        
        if not self.natural_key:
            return errors, 0
        
        keys_seen = []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):
                key_values = tuple(row.get(col, '') for col in self.natural_key)
                keys_seen.append(key_values)
        
        key_counts = Counter(keys_seen)
        duplicates = {k: count for k, count in key_counts.items() if count > 1}
        
        if duplicates:
            for key, count in list(duplicates.items())[:5]:
                errors.append(f"Duplicate key {dict(zip(self.natural_key, key))}: {count} occurrences")
            
            if len(duplicates) > 5:
                errors.append(f"... and {len(duplicates) - 5} more duplicate keys")
        
        return errors, len(duplicates)
    
    def _validate_required_fields(self, csv_file: str) -> Tuple[List[str], int]:
        """Validate required fields are present."""
        errors = []
        missing_count = 0
        
        if not self.natural_key:
            return errors, 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):
                for key_col in self.natural_key:
                    value = row.get(key_col, '').strip()
                    
                    if not value or value in ('', 'NULL', 'N/A', 'null'):
                        missing_count += 1
                        if len(errors) < 10:
                            errors.append(f"Row {row_num}: Missing required field '{key_col}'")
        
        if missing_count > 10:
            errors.append(f"... and {missing_count - 10} more rows with missing keys")
        
        return errors, missing_count
