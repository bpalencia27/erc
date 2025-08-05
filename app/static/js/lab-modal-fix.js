// Script de compatibilidad para modales
document.addEventListener('DOMContentLoaded', function() {
    // Solo aplicar si no existe modalManager
    if (!window.modalManager) {
        console.log('Usando lab-modal-fix como fallback para modales');
        
        // Fix para cerrar modales
        function closeModal(modalId) {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.style.display = 'none';
                modal.classList.remove('show');
                document.body.classList.remove('modal-open');
                
                // Remover backdrop si existe
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.remove();
                }
            }
        }
        
        // Agregar listeners a todos los botones de cerrar
        document.querySelectorAll('[data-dismiss="modal"], .close, .modal-close').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const modal = this.closest('.modal, .modal-backdrop');
                if (modal) {
                    closeModal(modal.id);
                }
            });
        });
        
        // Cerrar al presionar ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                document.querySelectorAll('.modal.show, .modal-backdrop.show').forEach(modal => {
                    closeModal(modal.id);
                });
            }
        });
    }
});