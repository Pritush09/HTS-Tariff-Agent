# HTS code and rate parser
import re
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class HTSParser:
    """Utility class for parsing and validating HTS numbers."""
    
    @staticmethod
    def normalize_hts_number(hts_number: str) -> str:
        """
        Normalize HTS number by removing spaces, dots, and ensuring proper format.
        
        Args:
            hts_number: Raw HTS number string
            
        Returns:
            Normalized HTS number
        """
        if not hts_number:
            return ""
        
        # Remove all non-numeric characters except dots
        cleaned = re.sub(r'[^\d.]', '', str(hts_number))
        
        # Remove dots
        cleaned = cleaned.replace('.', '')
        
        # Ensure we have at least 4 digits
        if len(cleaned) < 4:
            cleaned = cleaned.ljust(4, '0')
        
        return cleaned
    
    @staticmethod
    def format_hts_number(hts_number: str) -> str:
        """
        Format HTS number with proper dots for display.
        
        Args:
            hts_number: Normalized HTS number
            
        Returns:
            Formatted HTS number (e.g., 0101.30.00.00)
        """
        cleaned = HTSParser.normalize_hts_number(hts_number)
        
        if len(cleaned) >= 10:
            return f"{cleaned[:4]}.{cleaned[4:6]}.{cleaned[6:8]}.{cleaned[8:10]}"
        elif len(cleaned) >= 8:
            return f"{cleaned[:4]}.{cleaned[4:6]}.{cleaned[6:8]}"
        elif len(cleaned) >= 6:
            return f"{cleaned[:4]}.{cleaned[4:6]}"
        else:
            return cleaned
    
    @staticmethod
    def validate_hts_number(hts_number: str) -> Tuple[bool, str]:
        """
        Validate HTS number format.
        
        Args:
            hts_number: HTS number to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not hts_number:
            return False, "HTS number cannot be empty"
        
        normalized = HTSParser.normalize_hts_number(hts_number)
        
        if len(normalized) < 4:
            return False, "HTS number must have at least 4 digits"
        
        if len(normalized) > 10:
            return False, "HTS number cannot exceed 10 digits"
        
        if not normalized.isdigit():
            return False, "HTS number must contain only digits"
        
        return True, ""
    
    @staticmethod
    def extract_chapter(hts_number: str) -> Optional[str]:
        """
        Extract chapter number (first 2 digits) from HTS number.
        
        Args:
            hts_number: HTS number
            
        Returns:
            Chapter number or None if invalid
        """
        normalized = HTSParser.normalize_hts_number(hts_number)
        if len(normalized) >= 2:
            return normalized[:2]
        return None
    
    @staticmethod
    def extract_heading(hts_number: str) -> Optional[str]:
        """
        Extract heading (first 4 digits) from HTS number.
        
        Args:
            hts_number: HTS number
            
        Returns:
            Heading or None if invalid
        """
        normalized = HTSParser.normalize_hts_number(hts_number)
        if len(normalized) >= 4:
            return normalized[:4]
        return None
    
    @staticmethod
    def get_hts_hierarchy(hts_number: str) -> dict:
        """
        Get the hierarchical breakdown of an HTS number.
        
        Args:
            hts_number: HTS number
            
        Returns:
            Dictionary with chapter, heading, subheading, etc.
        """
        normalized = HTSParser.normalize_hts_number(hts_number)
        
        hierarchy = {
            'original': hts_number,
            'normalized': normalized,
            'formatted': HTSParser.format_hts_number(hts_number),
            'chapter': None,
            'heading': None,
            'subheading': None,
            'tariff_item': None,
            'statistical_suffix': None
        }
        
        if len(normalized) >= 2:
            hierarchy['chapter'] = normalized[:2]
        
        if len(normalized) >= 4:
            hierarchy['heading'] = normalized[:4]
        
        if len(normalized) >= 6:
            hierarchy['subheading'] = normalized[:6]
        
        if len(normalized) >= 8:
            hierarchy['tariff_item'] = normalized[:8]
        
        if len(normalized) >= 10:
            hierarchy['statistical_suffix'] = normalized[8:10]
        
        return hierarchy