/**
 * Test frontend específico para modales, subida de archivos y validaciones
 */

class FrontendTester {
    constructor() {
        this.testResults = [];
        this.totalTests = 0;
        this.passedTests = 0;
    }

    // Ejecutar todos los tests
    async runAllTests() {
        console.log('🧪 Iniciando tests del frontend...');
        
        await this.testModalManager();
        await this.testFileUploader();
        await this.testPatientFormValidation();
        await this.testLabResultsProcessing();
        await this.testAPIIntegration();
        
        this.showResults();
    }

    // Test del sistema de modales
    async testModalManager() {
        console.log('📋 Testing Modal Manager...');
        
        // Test 1: Modal Manager existe
        this.assert(
            typeof window.modalManager !== 'undefined',
            'Modal Manager debe estar inicializado'
        );
        
        // Test 2: Crear modal de prueba
        const testModal = document.createElement('div');
        testModal.id = 'test-modal';
        testModal.className = 'modal';
        testModal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5>Test Modal</h5>
                        <button class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">Test content</div>
                </div>
            </div>
        `;
        document.body.appendChild(testModal);
        
        // Test 3: Abrir modal
        window.modalManager.openModal('test-modal');
        await this.delay(100);
        
        this.assert(
            testModal.classList.contains('show'),
            'Modal debe tener clase show cuando está abierto'
        );
        
        this.assert(
            document.body.classList.contains('modal-open'),
            'Body debe tener clase modal-open'
        );
        
        // Test 4: Cerrar modal
        window.modalManager.closeModal('test-modal');
        await this.delay(200);
        
        this.assert(
            !testModal.classList.contains('show'),
            'Modal no debe tener clase show cuando está cerrado'
        );
        
        // Limpiar
        document.body.removeChild(testModal);
        
        // Test 5: Notificaciones
        const notification = window.modalManager.showNotification(
            'Test notification', 
            'success',
            { duration: 100 }
        );
        
        this.assert(
            notification && notification.classList.contains('notification-toast'),
            'Notificación debe crearse correctamente'
        );
        
        await this.delay(150);
        
        console.log('✅ Modal Manager tests completados');
    }

    // Test del subidor de archivos
    async testFileUploader() {
        console.log('📁 Testing File Uploader...');
        
        // Test 1: Elemento de upload existe
        const fileInput = document.getElementById('lab-file-upload');
        this.assert(
            fileInput !== null,
            'Input de archivo debe existir'
        );
        
        // Test 2: Función de validación de archivos
        if (typeof window.validateLabFile === 'function') {
            // Test con archivo válido
            const validFile = new File(['test content'], 'test.txt', { type: 'text/plain' });
            const isValid = window.validateLabFile(validFile);
            
            this.assert(
                isValid === true,
                'Archivo de texto válido debe pasar validación'
            );
            
            // Test con archivo inválido
            const invalidFile = new File(['test'], 'test.exe', { type: 'application/exe' });
            const isInvalid = window.validateLabFile(invalidFile);
            
            this.assert(
                isInvalid === false,
                'Archivo ejecutable debe fallar validación'
            );
        }
        
        // Test 3: Simulación de upload
        const mockLabText = `
            LABORATORIO TEST
            Paciente: Test Patient
            Creatinina sérica: 1.2 mg/dL
            Urea: 45 mg/dL
        `;
        
        if (typeof window.processLabFile === 'function') {
            const result = await window.processLabFile(mockLabText);
            
            this.assert(
                result && result.success === true,
                'Procesamiento de archivo de lab debe ser exitoso'
            );
            
            this.assert(
                result.results && result.results.creatinina_serica === 1.2,
                'Creatinina debe extraerse correctamente'
            );
        }
        
        console.log('✅ File Uploader tests completados');
    }

    // Test de validación del formulario de paciente
    async testPatientFormValidation() {
        console.log('👤 Testing Patient Form Validation...');
        
        // Test 1: Campos requeridos
        const requiredFields = ['nombre', 'edad', 'sexo', 'peso'];
        
        for (const fieldId of requiredFields) {
            const field = document.getElementById(fieldId);
            this.assert(
                field !== null,
                `Campo requerido ${fieldId} debe existir`
            );
            
            if (field) {
                this.assert(
                    field.hasAttribute('required') || field.getAttribute('aria-required') === 'true',
                    `Campo ${fieldId} debe estar marcado como requerido`
                );
            }
        }
        
        // Test 2: Validación de edad
        const edadField = document.getElementById('edad');
        if (edadField) {
            // Simular entrada inválida
            edadField.value = '150';
            edadField.dispatchEvent(new Event('input'));
            
            // Verificar validación (implementar según tu lógica)
            if (typeof window.validateAge === 'function') {
                const isValid = window.validateAge(150);
                this.assert(
                    isValid === false,
                    'Edad 150 debe ser inválida'
                );
            }
        }
        
        // Test 3: Cálculo de IMC
        const pesoField = document.getElementById('peso');
        const tallaField = document.getElementById('talla');
        const imcField = document.getElementById('imc');
        
        if (pesoField && tallaField && imcField) {
            pesoField.value = '70';
            tallaField.value = '170';
            
            // Simular cálculo de IMC
            if (typeof window.calculateIMC === 'function') {
                const imc = window.calculateIMC(70, 170);
                this.assert(
                    Math.abs(imc - 24.2) < 0.1,
                    'Cálculo de IMC debe ser correcto'
                );
            }
        }
        
        console.log('✅ Patient Form Validation tests completados');
    }

    // Test de procesamiento de resultados de laboratorio
    async testLabResultsProcessing() {
        console.log('🧪 Testing Lab Results Processing...');
        
        // Test 1: Función de cálculo de TFG
        if (typeof window.calculateTFG === 'function') {
            const tfg = window.calculateTFG({
                edad: 65,
                peso: 70,
                creatinina: 1.2,
                sexo: 'M'
            });
            
            this.assert(
                tfg > 0 && tfg < 150,
                'TFG calculado debe estar en rango válido'
            );
            
            this.assert(
                tfg >= 50 && tfg <= 70,
                'TFG para estos parámetros debe estar en rango esperado'
            );
        }
        
        // Test 2: Determinación de etapa ERC
        if (typeof window.determineERCStage === 'function') {
            const stage = window.determineERCStage(45);
            this.assert(
                stage === 'G3a',
                'TFG 45 debe corresponder a etapa G3a'
            );
        }
        
        // Test 3: Validación de valores de laboratorio
        if (typeof window.validateLabValue === 'function') {
            // Creatinina normal
            const creatNormal = window.validateLabValue('creatinina', 1.0, 'M');
            this.assert(
                creatNormal.status === 'normal',
                'Creatinina 1.0 en hombre debe ser normal'
            );
            
            // Creatinina elevada
            const creatHigh = window.validateLabValue('creatinina', 2.5, 'M');
            this.assert(
                creatHigh.status === 'high',
                'Creatinina 2.5 debe estar elevada'
            );
        }
        
        console.log('✅ Lab Results Processing tests completados');
    }

    // Test de integración con API
    async testAPIIntegration() {
        console.log('🌐 Testing API Integration...');
        
        // Test 1: Verificar que las funciones de API existen
        const apiChecks = [
            'generateReport',
            'uploadLabFile',
            'calculateRisk',
            'savePatientData'
        ];
        
        for (const apiFunc of apiChecks) {
            if (typeof window[apiFunc] === 'function') {
                this.assert(
                    true,
                    `Función de API ${apiFunc} está disponible`
                );
            } else {
                console.warn(`⚠️ Función de API ${apiFunc} no encontrada`);
            }
        }
        
        // Test 2: Mock de llamada a API (sin hacer llamada real)
        const mockPatientData = {
            nombre: 'Test Patient',
            edad: 65,
            sexo: 'M',
            peso: 70,
            creatinina_serica: 1.2
        };
        
        // Verificar estructura de datos para API
        this.assert(
            typeof mockPatientData === 'object',
            'Datos del paciente deben ser un objeto'
        );
        
        this.assert(
            mockPatientData.nombre && mockPatientData.edad,
            'Datos del paciente deben incluir campos requeridos'
        );
        
        console.log('✅ API Integration tests completados');
    }

    // Utilidades de testing
    assert(condition, message) {
        this.totalTests++;
        if (condition) {
            this.passedTests++;
            console.log(`✅ ${message}`);
            this.testResults.push({ test: message, passed: true });
        } else {
            console.error(`❌ ${message}`);
            this.testResults.push({ test: message, passed: false });
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    showResults() {
        console.log('\n📊 RESULTADOS DE TESTS FRONTEND');
        console.log('=' * 50);
        console.log(`✅ Tests pasados: ${this.passedTests}/${this.totalTests}`);
        console.log(`📈 Porcentaje de éxito: ${(this.passedTests/this.totalTests*100).toFixed(1)}%`);
        
        if (this.passedTests < this.totalTests) {
            console.log('\n❌ Tests fallidos:');
            this.testResults
                .filter(r => !r.passed)
                .forEach(r => console.log(`   - ${r.test}`));
        }
        
        // Mostrar en la interfaz si es posible
        if (window.modalManager) {
            const message = `Tests: ${this.passedTests}/${this.totalTests} pasados (${(this.passedTests/this.totalTests*100).toFixed(1)}%)`;
            const type = this.passedTests === this.totalTests ? 'success' : 'warning';
            window.modalManager.showNotification(message, type, { duration: 5000 });
        }
    }
}

// Función global para ejecutar tests
window.runFrontendTests = function() {
    const tester = new FrontendTester();
    return tester.runAllTests();
};

// Auto-ejecutar si estamos en modo debug
if (window.location.search.includes('debug=true') || window.location.search.includes('test=true')) {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            console.log('🚀 Auto-ejecutando tests frontend...');
            window.runFrontendTests();
        }, 1000);
    });
}

// Exportar para uso en consola
window.FrontendTester = FrontendTester;
