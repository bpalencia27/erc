"""
Project configuration for RCV-CO system
"""
from pathlib import Path
from typing import Dict, Any

# Base configuration
BASE_CONFIG: Dict[str, Any] = {
    "app_name": "RCV-CO",
    "version": "2.0.0",
    "description": "Clinical Risk Assessment System for CKD",
}

# Paths configuration
PATHS = {
    "base_dir": Path(__file__).parent.parent,
    "data_dir": Path(__file__).parent.parent / "data",
    "logs_dir": Path(__file__).parent.parent / "logs",
}

# Create required directories
for path in PATHS.values():
    path.mkdir(exist_ok=True)

# Clinical configuration
CLINICAL_CONFIG = {
    "ckd_stages": ["G1", "G2", "G3a", "G3b", "G4", "G5"],
    "cv_risk_levels": ["low", "medium", "high", "very_high"],
    "default_lab_validity_days": 180,
}

# Reporting configuration
REPORT_CONFIG = {
    "template_dir": PATHS["base_dir"] / "templates",
    "output_dir": PATHS["data_dir"] / "reports",
    "default_language": "es",
}

# System configuration
SYSTEM_CONFIG = {
    "log_level": "INFO",
    "max_retries": 3,
    "timeout": 30,
}
