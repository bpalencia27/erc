"""
Document extraction registry and factory.
"""

from pathlib import Path
from typing import Dict, Type, Optional

from .extractors._base import DocumentExtractor
from .extractors.pdf import PDFExtractor
from .extractors.text import TextExtractor

class ExtractorRegistry:
    """Registry for document extractors."""
    
    def __init__(self):
        self._extractors: Dict[str, DocumentExtractor] = {}
        
        # Register default extractors
        self.register_extractor(PDFExtractor())
        self.register_extractor(TextExtractor())

    def register_extractor(self, extractor: DocumentExtractor):
        """
        Register a new document extractor.
        
        Args:
            extractor (DocumentExtractor): Extractor instance to register
        """
        self._extractors[extractor.__class__.__name__] = extractor

    def get_extractor(self, file_path: Path) -> Optional[DocumentExtractor]:
        """
        Get appropriate extractor for given file.
        
        Args:
            file_path (Path): Path to document file
            
        Returns:
            Optional[DocumentExtractor]: Appropriate extractor or None if no support
        """
        for extractor in self._extractors.values():
            if extractor.supports_format(file_path):
                return extractor
        return None
