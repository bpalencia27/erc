"""
Text document extraction implementation.
"""

import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from ._base import (
    DocumentExtractor, 
    ExtractionError,
    FormatNotSupportedError,
    FileNotFoundError
)

class TextExtractor(DocumentExtractor):
    """Extract content from text documents."""
    
    SUPPORTED_EXTENSIONS = {'.txt', '.text', '.log'}
    ENCODINGS = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    def supports_format(self, file_path: Path) -> bool:
        """Check if file is a supported text format."""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def extract(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract content from a text file.
        
        Args:
            file_path (Path): Path to text file
            
        Returns:
            Dict[str, Any]: Extracted content with metadata
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            FormatNotSupportedError: If format not supported
            ExtractionError: If extraction fails
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Text file not found: {file_path}")
            
        if not self.supports_format(file_path):
            raise FormatNotSupportedError(f"Unsupported text format: {file_path}")

        # Try encodings in order
        decode_errors = []
        for encoding in self.ENCODINGS:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    text = file.read()
                    
                text = text.strip()
                if not text:
                    logging.warning(f"Empty text file: {file_path}")
                
                return {
                    'text': text,
                    'metadata': {
                        'source': 'text',
                        'encoding': encoding,
                        'size_bytes': file_path.stat().st_size,
                        'filename': file_path.name
                    }
                }
            except UnicodeDecodeError as e:
                decode_errors.append(f"{encoding}: {str(e)}")
                continue
                
        # If we get here, no encoding worked
        raise ExtractionError(
            f"Failed to decode text file with any supported encoding.\n"
            f"Tried:\n{chr(10).join(decode_errors)}"
        )

        raise ExtractionError(f"Failed to decode text file with any supported encoding: {file_path}")
