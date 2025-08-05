/**
 * Funciones JavaScript principales para ERC Insight
 */

// Ejecutar cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips y popovers de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Configurar tiempo de desaparición para alertas
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

/**
 * Función para calcular la TFG en tiempo real
 * Usada en formularios de pacientes
 */
function calculateTFG() {
    const edad = document.getElementById('edad').value;
    const peso = document.getElementById('peso').value;
    const creatinina = document.getElementById('creatinina').value;
    const sexo = document.querySelector('input[name="sexo"]:checked').value;
    
    if (edad && peso && creatinina) {
        // Llamar a la API para calcular TFG
        fetch('/patient/api/tfg', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                edad: edad,
                peso: peso,
                creatinina: creatinina,
                sexo: sexo
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('tfg-result').textContent = data.tfg;
                document.getElementById('erc-stage').textContent = data.etapa_erc.toUpperCase();
                document.getElementById('tfg-container').classList.remove('d-none');
            }
        })
        .catch(error => {
            console.error('Error al calcular TFG:', error);
        });
    }
}

/**
 * Función para confirmar acciones destructivas
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}
