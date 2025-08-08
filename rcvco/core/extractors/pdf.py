"""
PDF document extraction implementation.
"""

import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from ._base import DocumentExtractor, ExtractionError

class PDFExtractor(DocumentExtractor):
    """Extract content from PDF documents."""
    
    def __init__(self, use_pdfplumber: bool = False):
        """
        Initialize PDF extractor.
        
        Args:
            use_pdfplumber (bool): If True, use pdfplumber instead of PyPDF2
        """
        self.use_pdfplumber = use_pdfplumber
        self._extractor = None

    def supports_format(self, file_path: Path) -> bool:
        """Check if file is a PDF."""
        return file_path.suffix.lower() == '.pdf'

    def extract(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract content from a PDF file.
        
        Args:
            file_path (Path): Path to PDF file
            
        Returns:
            Dict[str, Any]: Extracted content with metadata
            
        Raises:
            ExtractionError: If extraction fails
        """
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
            
        if not self.supports_format(file_path):
            raise FormatNotSupportedError(f"Not a PDF file: {file_path}")

        try:
            if self.use_pdfplumber:
                return self._extract_with_pdfplumber(file_path)
            return self._extract_with_pypdf2(file_path)
        except Exception as e:
            raise ExtractionError(f"Failed to extract PDF content: {e}")

    def _extract_with_pypdf2(self, file_path: Path) -> Dict[str, Any]:
        """Extract using PyPDF2."""
        try:
            import PyPDF2
        except ImportError:
            logging.warning("PyPDF2 not installed, falling back to pdfplumber")
            return self._extract_with_pdfplumber(file_path)

        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                metadata = {
                    'source': 'PyPDF2',
                    'page_count': len(reader.pages),
                    'size_bytes': file_path.stat().st_size
                }
                
                # Extract text from all pages
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                    
                text = text.strip()
                if not text:
                    logging.warning("PyPDF2 extracted empty text, trying pdfplumber")
                    return self._extract_with_pdfplumber(file_path)
                    
                return {
                    'text': text,
                    'metadata': metadata
                }
        except Exception as e:
            logging.warning(f"PyPDF2 extraction failed: {e}, trying pdfplumber")
            return self._extract_with_pdfplumber(file_path)

    def _extract_with_pdfplumber(self, file_path: Path) -> Dict[str, Any]:
        """Extract using pdfplumber."""
        try:
            import pdfplumber
        except ImportError:
            raise ExtractionError(
                "No PDF extraction library available. Please install either PyPDF2 or pdfplumber."
            )

        try:
            text = ""
            metadata = {
                'source': 'pdfplumber',
                'size_bytes': file_path.stat().st_size
            }
            
            with pdfplumber.open(file_path) as pdf:
                metadata['page_count'] = len(pdf.pages)
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
                        
            text = text.strip()
            if not text:
                raise ExtractionError("No text content extracted from PDF")
            
            return {
                'text': text,
                'metadata': metadata
            }
        except Exception as e:
            raise ExtractionError(f"pdfplumber extraction failed: {str(e)}")
