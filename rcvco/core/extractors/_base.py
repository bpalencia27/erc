"""
Base classes for document extraction.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path

class DocumentExtractor(ABC):
    """Base class for all document extractors."""
    
    @abstractmethod
    def extract(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract content from a document file.
        
        Args:
            file_path (Path): Path to the document file
            
        Returns:
            Dict[str, Any]: Extracted content in a structured format
            
        Raises:
            ExtractionError: If extraction fails
        """
        pass

    @abstractmethod
    def supports_format(self, file_path: Path) -> bool:
        """
        Check if this extractor supports the given file format.
        
        Args:
            file_path (Path): Path to check
            
        Returns:
            bool: True if supported, False otherwise
        """
        pass

class ExtractionError(Exception):
    """Base exception for extraction errors."""
    pass

class FormatNotSupportedError(ExtractionError):
    """Exception raised when trying to extract from an unsupported format."""
    pass

class FileNotFoundError(ExtractionError):
    """Exception raised when the file to extract from doesn't exist."""
    pass
