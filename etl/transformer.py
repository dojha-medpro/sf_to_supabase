"""CSV Transformation Engine - Applies mappings and coercions."""
import csv
import re
from datetime import datetime, date
from dateutil import parser as date_parser
from io import StringIO
from typing import Dict, List, Any, Optional
from .encoding_utils import detect_encoding


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
        
        encoding = detect_encoding(input_file)
        
        with open(input_file, 'r', encoding=encoding) as infile:
            reader = csv.DictReader(infile)
            
            if not reader.fieldnames:
                raise ValueError("CSV file has no headers")
            
            mapped_headers = self._map_headers(reader.fieldnames)
            mapped_headers.extend(['_partition_date', '_file_name', '_source_report', '_extract_ts'])
            
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
        
        return transformed
    
    def _apply_coercion(self, column_name: str, value: str) -> Any:
        """Apply coercion rules to a value."""
        if not value or value in self.null_like:
            return None
        
        coercion = self.coercions.get(column_name, '')
        
        if not coercion:
            return value
        
        rules = coercion.split('|')
        
        for rule in rules:
            rule = rule.strip()
            
            if rule == 'trim':
                value = str(value).strip() if value else value
            elif rule == 'lower':
                value = str(value).lower() if value else value
            elif rule == 'boolean':
                result = self._to_boolean(value)
                value = result if result is not None else value
            elif rule == 'date':
                result = self._to_date(value)
                value = result if result is not None else value
            elif rule == 'timestamptz':
                result = self._to_timestamptz(value)
                value = result if result is not None else value
            elif rule == 'numeric':
                result = self._to_numeric(value)
                value = result if result is not None else value
        
        return value
    
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
