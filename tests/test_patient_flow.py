# e2e_tests/test_patient_flow.py
import pytest
from playwright.sync_api import Page, expect

@pytest.fixture(scope="session")
def browser_context(playwright):
    browser = playwright.chromium.launch()
    context = browser.new_context()
    yield context
    context.close()
    browser.close()

def test_patient_registration_flow(page: Page):
    """Test completo del flujo de registro de paciente"""
    # Navegar a la página
    page.goto("http://localhost:5000")
    
    # Llenar formulario
    page.fill("#nombre", "Juan Pérez")
    page.fill("#edad", "65")
    page.select_option("#sexo", "m")
    page.fill("#peso", "75")
    page.fill("#creatinina", "1.5")
    
    # Verificar cálculo TFG dinámico
    expect(page.locator("#tfg-display")).not_to_be_empty()
    
    # Submit y verificar respuesta
    page.click("#generate-report-btn")
    expect(page.locator("#report-output")).to_be_visible(timeout=10000)

def test_lab_upload_flow(page: Page):
    """Test de carga y procesamiento de laboratorio"""
    page.goto("http://localhost:5000")
    
    # Subir archivo
    page.set_input_files("#lab-file-upload", "test_files/lab_sample.pdf")
    
    # Verificar procesamiento
    expect(page.locator(".lab-result-card")).to_be_visible()
    
    # Verificar autocompletado
    expect(page.locator("#nombre")).not_to_have_value("")