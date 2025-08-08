"""
Tests for document extraction functionality.
"""

import pytest
from pathlib import Path
from datetime import datetime

from rcvco.core.extractors._base import DocumentExtractor, ExtractionError
from rcvco.core.extractors.pdf import PDFExtractor
from rcvco.core.extractors.text import TextExtractor
from rcvco.core.parser import LabParser, LabReport
from rcvco.core.processor import DocumentProcessor

class MockExtractor(DocumentExtractor):
    """Mock extractor for testing."""
    
    def __init__(self, supports=True, content="Test content"):
        self.supports = supports
        self.content = content
        
    def supports_format(self, file_path: Path) -> bool:
        return self.supports
        
    def extract(self, file_path: Path) -> dict:
        return {'text': self.content}

def test_extractor_registry():
    """Test extractor registration and lookup."""
    from rcvco.core.registry import ExtractorRegistry
    
    registry = ExtractorRegistry()
    mock_extractor = MockExtractor()
    registry.register_extractor(mock_extractor)
    
    path = Path('test.txt')
    extractor = registry.get_extractor(path)
    assert extractor is not None
    
def test_lab_parser():
    """Test lab results parsing."""
    parser = LabParser()
    
    # Test with minimal valid content
    content = """
    Fecha: 2023-01-15
    Paciente: Juan Pérez
    ID: 12345
    Edad: 45
    Género: Masculino
    
    Creatinina: 1.2 mg/dL
    Glucosa: 95 mg/dL
    """
    
    report = parser.parse(content, Path('test.txt'))
    assert report.date == datetime(2023, 1, 15)
    assert report.patient_name == "Juan Pérez"
    assert report.patient_id == "12345"
    assert report.patient_age == 45
    assert report.patient_gender == "M"
    assert len(report.values) == 2

def test_pdf_extractor():
    """Test PDF extraction."""
    extractor = PDFExtractor()
    
    # Test format support
    assert extractor.supports_format(Path('test.pdf'))
    assert not extractor.supports_format(Path('test.txt'))
    
    # Test extraction errors
    with pytest.raises(FileNotFoundError):
        extractor.extract(Path('nonexistent.pdf'))

def test_text_extractor():
    """Test text extraction."""
    extractor = TextExtractor()
    
    # Test format support
    assert extractor.supports_format(Path('test.txt'))
    assert not extractor.supports_format(Path('test.pdf'))
    
    # Test supported extensions
    assert all(ext.startswith('.') for ext in extractor.SUPPORTED_EXTENSIONS)

def test_document_processor():
    """Test end-to-end document processing."""
    processor = DocumentProcessor()
    
    # Register mock extractor
    mock_content = """
    Fecha: 2023-01-15
    Paciente: Test Patient
    Creatinina: 1.0 mg/dL
    """
    processor.registry.register_extractor(MockExtractor(content=mock_content))
    
    # Process mock document
    report = processor.process_document('test.txt')
    assert isinstance(report, LabReport)
    assert report.date == datetime(2023, 1, 15)
    assert report.patient_name == "Test Patient"
    assert len(report.values) == 1
