"""YAML Mapping Parser - Reads and parses mapping files."""
import yaml
from pathlib import Path
from typing import Dict, List, Any


class MappingParser:
    """Parses YAML mapping files for CSV transformation."""
    
    def __init__(self, mappings_dir: str = "Mappings"):
        self.mappings_dir = Path(mappings_dir)
    
    def get_available_mappings(self) -> List[str]:
        """Get list of available mapping files."""
        if not self.mappings_dir.exists():
            return []
        return [f.stem for f in self.mappings_dir.glob("*.yaml")]
    
    def load_mapping(self, mapping_name: str) -> Dict[str, Any]:
        """Load a mapping file by name."""
        mapping_file = self.mappings_dir / f"{mapping_name}.yaml"
        
        if not mapping_file.exists():
            raise FileNotFoundError(f"Mapping file not found: {mapping_file}")
        
        with open(mapping_file, 'r') as f:
            mapping = yaml.safe_load(f)
        
        return mapping
    
    def get_target_table(self, mapping: Dict[str, Any]) -> str:
        """Extract target table name from mapping."""
        target_object = mapping.get('target_object')
        if not target_object:
            raise ValueError("Mapping missing 'target_object' field")
        return f"staging.{target_object}"
    
    def get_column_mapping(self, mapping: Dict[str, Any]) -> Dict[str, str]:
        """Get source header to target column mapping."""
        return mapping.get('columns', {})
    
    def get_coercions(self, mapping: Dict[str, Any]) -> Dict[str, str]:
        """Get column coercion rules."""
        return mapping.get('coercions', {})
    
    def get_null_like_values(self, mapping: Dict[str, Any]) -> List[str]:
        """Get list of values to treat as NULL."""
        return mapping.get('null_like', ["", "NULL", "N/A", "n/a", "null"])
    
    def get_natural_key(self, mapping: Dict[str, Any]) -> List[str]:
        """Get natural key columns."""
        return mapping.get('natural_key', [])
    
    def get_reject_rules(self, mapping: Dict[str, Any]) -> List[str]:
        """Get reject rules."""
        return mapping.get('reject_rules', [])
