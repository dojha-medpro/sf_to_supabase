"""CSV utility functions for handling duplicate headers and other edge cases."""
from typing import List
from collections import Counter


def normalize_duplicate_headers(headers: List[str]) -> List[str]:
    """
    Normalize duplicate headers by adding __2, __3, etc. suffixes.
    
    Example:
        ['Name', 'ID', 'ID', 'Status', 'ID'] 
        -> ['Name', 'ID', 'ID__2', 'Status', 'ID__3']
    
    Args:
        headers: List of column headers (may contain duplicates)
        
    Returns:
        List of unique headers with suffixes added to duplicates
    """
    seen = {}
    normalized = []
    
    for header in headers:
        if header not in seen:
            seen[header] = 1
            normalized.append(header)
        else:
            seen[header] += 1
            normalized.append(f"{header}__{seen[header]}")
    
    return normalized
