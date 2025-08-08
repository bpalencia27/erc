"""
Main entry point for document extraction and parsing.
"""

from pathlib import Path
from typing import Dict, Any

from .registry import ExtractorRegistry
from .parser import LabParser, LabReport

class DocumentProcessor:
    """Main document processing class."""
    
    def __init__(self):
        self.registry = ExtractorRegistry()
        self.parser = LabParser()

    def process_document(self, file_path: str) -> LabReport:
        """
        Process a document file and extract lab results.
        
        Args:
            file_path (str): Path to document file
            
        Returns:
            LabReport: Structured lab report data
            
        Raises:
            ValueError: If no suitable extractor found for file
            ExtractionError: If extraction fails
        """
        path = Path(file_path)
        
        # Get appropriate extractor
        extractor = self.registry.get_extractor(path)
        if not extractor:
            raise ValueError(f"No suitable extractor found for: {path}")
            
        # Extract raw content
        content = extractor.extract(path)
        
        # Parse lab results
        return self.parser.parse(content['text'], path)
