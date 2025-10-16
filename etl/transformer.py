"""CSV Transformation Engine - Applies mappings and coercions."""
import csv
import re
from datetime import datetime, date
from dateutil import parser as date_parser
from io import StringIO
from typing import Dict, List, Any, Optional
from .encoding_utils import detect_encoding
from .csv_utils import normalize_duplicate_headers


class CSVTransformer:
    """Transforms CSV data based on YAML mapping specifications."""
    
    def __init__(self, mapping: Dict[str, Any]):
        self.mapping = mapping
        self.column_mapping = mapping.get('columns', {})
        self.coercions = mapping.get('coercions', {})
        self.null_like = mapping.get('null_like', ["", "NULL", "N/A", "n/a", "null"])
    
    def transform_csv(self, input_file: str, output_file: str, 
                     partition_date: date, file_name: str, 
                     source_report: str) -> tuple[int, List[str]]:
        """
        Transform a CSV file according to mapping.
        
        Returns:
            (row_count, errors) tuple
        """
        errors = []
        row_count = 0
        
        encoding, errors_mode = detect_encoding(input_file)
        
        with open(input_file, 'r', encoding=encoding, errors=errors_mode) as infile:
            reader = csv.DictReader(infile)
            
            if not reader.fieldnames:
                raise ValueError("CSV file has no headers")
            
            # Normalize duplicate headers (add __2, __3 suffixes automatically)
            original_headers = list(reader.fieldnames)
            normalized_headers = normalize_duplicate_headers(original_headers)
            reader.fieldnames = normalized_headers
            
            mapped_headers = self._map_headers(normalized_headers)
            mapped_headers.extend(['_partition_date', '_file_name', '_source_report', '_extract_ts', '_mapping_version', '_raw_hash'])
            
            with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=mapped_headers)
                writer.writeheader()
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        transformed_row = self._transform_row(
                            row, partition_date, file_name, source_report
                        )
                        writer.writerow(transformed_row)
                        row_count += 1
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
        
        return row_count, errors
    
    def _map_headers(self, source_headers: Any) -> List[str]:
        """Map source headers to target column names."""
        mapped = []
        for header in source_headers:
            if header in self.column_mapping:
                mapped.append(self.column_mapping[header])
        return mapped
    
    def _transform_row(self, row: Dict[str, str], partition_date: date,
                      file_name: str, source_report: str) -> Dict[str, Any]:
        """Transform a single row."""
        transformed = {}
        
        for source_col, target_col in self.column_mapping.items():
            value = row.get(source_col, '')
            
            if value in self.null_like:
                transformed[target_col] = None
            else:
                transformed[target_col] = self._apply_coercion(target_col, value)
        
        transformed['_partition_date'] = partition_date.isoformat()
        transformed['_file_name'] = file_name
        transformed['_source_report'] = source_report
        transformed['_extract_ts'] = datetime.now().isoformat()
        transformed['_mapping_version'] = None  # TODO: Add version tracking
        transformed['_raw_hash'] = None  # TODO: Add row hashing for deduplication
        
        return transformed
    
    def _apply_coercion(self, column_name: str, value: str) -> Any:
        """Apply coercion rules to a value."""
        if not value or value in self.null_like:
            return None
        
        coercion = self.coercions.get(column_name, '')
        
        if not coercion:
            return value
        
        rules = coercion.split('|')
        result: Any = value
        
        for rule in rules:
            rule = rule.strip()
            
            if rule == 'trim':
                result = str(result).strip() if result else result
            elif rule == 'lower':
                result = str(result).lower() if result else result
            elif rule == 'boolean':
                bool_result = self._to_boolean(str(result))
                if bool_result is not None:
                    result = bool_result
            elif rule == 'date':
                date_result = self._to_date(str(result))
                result = date_result if date_result is not None else result
            elif rule == 'timestamptz':
                ts_result = self._to_timestamptz(str(result))
                result = ts_result if ts_result is not None else result
            elif rule == 'numeric':
                num_result = self._to_numeric(str(result))
                if num_result is not None:
                    result = num_result
        
        return result
    
    def _to_boolean(self, value: str) -> Optional[bool]:
        """Convert string to boolean."""
        if not value:
            return None
        
        value_lower = str(value).lower().strip()
        
        if value_lower in ('true', 'yes', '1', 't', 'y'):
            return True
        elif value_lower in ('false', 'no', '0', 'f', 'n'):
            return False
        else:
            return None
    
    def _to_date(self, value: str) -> Optional[str]:
        """Convert string to ISO date."""
        if not value:
            return None
        
        try:
            parsed = date_parser.parse(value)
            return parsed.date().isoformat()
        except:
            return None
    
    def _to_timestamptz(self, value: str) -> Optional[str]:
        """Convert string to ISO timestamp."""
        if not value:
            return None
        
        try:
            parsed = date_parser.parse(value)
            return parsed.isoformat()
        except:
            return None
    
    def _to_numeric(self, value: str) -> Optional[float]:
        """Convert string to numeric, stripping currency symbols."""
        if not value:
            return None
        
        cleaned = re.sub(r'[$,\s]', '', str(value))
        
        try:
            return float(cleaned)
        except:
            return None
