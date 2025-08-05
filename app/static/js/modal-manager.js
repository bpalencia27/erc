/**
 * Gestor completo de modales para el proyecto ERC
 * Maneja apertura, cierre, eventos, notificaciones y edición manual de laboratorios importados
 */
class ModalManager {
    constructor() {
        this.activeModals = new Set();
        this.modalStack = [];
        this.initialized = false;
        this.init();
    }
    
    init() {
        if (this.initialized) return;
        this.setupGlobalListeners();
        this.setupExistingModals();
        this.initialized = true;
    }
    
    setupGlobalListeners() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modalStack.length > 0) {
                e.preventDefault();
                const lastModal = this.modalStack[this.modalStack.length - 1];
                this.closeModal(lastModal);
            }
        });
        
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-backdrop') || e.target.classList.contains('modal')) {
                const modal = e.target.closest('.modal') || document.querySelector('.modal.show');
                if (modal && e.target === modal) {
                    this.closeModal(modal.id || modal);
                }
            }
        });
    }
    
    setupExistingModals() {
        const closeSelectors = [
            '[data-dismiss="modal"]', '[data-bs-dismiss="modal"]', '.close', '.btn-close', 
            '.modal-close', '.modal-header .close', 'button[aria-label="Close"]'
        ];
        
        document.addEventListener('click', (e) => {
            if (closeSelectors.some(selector => e.target.matches(selector))) {
                e.preventDefault();
                e.stopPropagation();
                const modal = e.target.closest('.modal, .modal-dialog, [role="dialog"]');
                if (modal) {
                    const modalElement = modal.classList.contains('modal') ? modal : modal.closest('.modal');
                    if (modalElement) {
                        this.closeModal(modalElement.id || modalElement);
                    }
                }
            }
        });
        
        // Edición manual de laboratorios importados
        document.addEventListener('change', (e) => {
            if (e.target.matches('.lab-editable-toggle')) {
                const labCard = e.target.closest('.lab-card');
                if (labCard) {
                    const editable = e.target.checked;
                    labCard.querySelectorAll('input, select, textarea').forEach(input => {
                        input.readOnly = !editable;
                        input.disabled = !editable;
                        if (editable) {
                            input.classList.remove('bg-gray-100', 'field-locked');
                        } else {
                            input.classList.add('bg-gray-100', 'field-locked');
                        }
                    });
                }
            }
        });
    }
    
    openModal(modalIdOrElement) {
        let modal;
        let modalId;
        
        if (typeof modalIdOrElement === 'string') {
            modalId = modalIdOrElement;
            modal = document.getElementById(modalId);
        } else {
            modal = modalIdOrElement;
            modalId = modal.id || `modal-${Date.now()}`;
        }
        
        if (!modal) {
            console.error(`Modal no encontrado:`, modalIdOrElement);
            return;
        }
        
        this.modalStack.push(modalId);
        this.activeModals.add(modalId);
        
        modal.style.display = 'block';
        modal.classList.add('show');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('role', 'dialog');
        document.body.classList.add('modal-open');
        
        // Añadir el backdrop si no existe
        if (!document.querySelector('.modal-backdrop')) {
            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop fade show';
            document.body.appendChild(backdrop);
        }
        
        modal.dispatchEvent(new CustomEvent('modal:opened', { detail: { modalId } }));
    }
    
    closeModal(modalIdOrElement) {
        let modal;
        let modalId;
        
        if (typeof modalIdOrElement === 'string') {
            modalId = modalIdOrElement;
            modal = document.getElementById(modalId);
        } else {
            modal = modalIdOrElement;
            modalId = modal?.id;
        }
        
        if (!modal) {
            console.warn(`Modal no encontrado para cerrar:`, modalIdOrElement);
            return;
        }
        
        this.modalStack = this.modalStack.filter(id => id !== modalId);
        this.activeModals.delete(modalId);
        
        modal.classList.remove('show');
        modal.classList.add('fade');
        
        if (this.modalStack.length === 0) {
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.classList.remove('show');
                setTimeout(() => backdrop.remove(), 150);
            }
            document.body.classList.remove('modal-open');
        }
        
        setTimeout(() => {
            modal.style.display = 'none';
            modal.classList.remove('fade');
            modal.removeAttribute('aria-modal');
            modal.dispatchEvent(new CustomEvent('modal:closed', { detail: { modalId } }));
        }, 150);
    }
    
    showNotification(message, type = 'info', options = {}) {
        const defaults = { 
            duration: 5000, 
            position: 'top-right', 
            showClose: true, 
            animate: true 
        };
        const settings = { ...defaults, ...options };
        const notificationId = `notification-${Date.now()}`;
        const iconMap = { 
            success: 'fa-check-circle', 
            error: 'fa-exclamation-circle', 
            warning: 'fa-exclamation-triangle', 
            info: 'fa-info-circle' 
        };
        
        const notificationHtml = `
            <div id="${notificationId}" class="notification-toast alert alert-${type} ${settings.animate ? 'notification-animate' : ''}" style="position: fixed; z-index: 9999; min-width: 300px; max-width: 500px;">
                <div class="d-flex align-items-center">
                    <i class="fas ${iconMap[type] || iconMap.info} me-2"></i>
                    <div class="flex-grow-1">${message}</div>
                    ${settings.showClose ? `<button type="button" class="btn-close btn-sm ms-2" aria-label="Close"></button>` : ''}
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', notificationHtml);
        const notification = document.getElementById(notificationId);
        
        this.positionNotification(notification, settings.position);
        
        if (settings.showClose) {
            const closeBtn = notification.querySelector('.btn-close');
            closeBtn.addEventListener('click', () => { 
                this.removeNotification(notification); 
            });
        }
        
        if (settings.duration > 0) {
            setTimeout(() => { 
                this.removeNotification(notification); 
            }, settings.duration);
        }
        
        return notification;
    }
    
    positionNotification(notification, position) {
        const positions = {
            'top-right': { top: '20px', right: '20px' },
            'top-left': { top: '20px', left: '20px' },
            'bottom-right': { bottom: '20px', right: '20px' },
            'bottom-left': { bottom: '20px', left: '20px' },
            'top-center': { top: '20px', left: '50%', transform: 'translateX(-50%)' },
            'bottom-center': { bottom: '20px', left: '50%', transform: 'translateX(-50%)' }
        };
        
        const posStyle = positions[position] || positions['top-right'];
        Object.assign(notification.style, posStyle);
        
        const existingNotifications = document.querySelectorAll('.notification-toast');
        let offset = 0;
        
        existingNotifications.forEach(existing => {
            if (existing !== notification && existing.style[posStyle.top ? 'top' : 'bottom']) {
                offset += existing.offsetHeight + 10;
            }
        });
        
        if (posStyle.top) {
            notification.style.top = `${parseInt(posStyle.top) + offset}px`;
        } else {
            notification.style.bottom = `${parseInt(posStyle.bottom) + offset}px`;
        }
    }
    
    removeNotification(notification) {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }
    
    closeAllModals() {
        [...this.modalStack].reverse().forEach(modalId => { 
            this.closeModal(modalId); 
        });
    }
    
    hasOpenModals() { 
        return this.modalStack.length > 0; 
    }
    
    getActiveModals() { 
        return [...this.activeModals]; 
    }
}

// Añadir estilos CSS para animaciones y visualización
const modalStyles = document.createElement('style');
modalStyles.textContent = `
    @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
    @keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
    .notification-animate { animation: slideIn 0.3s ease-out; }
    .modal.fade { transition: opacity 0.15s linear; }
    .modal.show { opacity: 1; }
    .modal-backdrop.fade { transition: opacity 0.15s linear; }
    .modal-backdrop.show { opacity: 0.5; }
    .notification-toast { box-shadow: 0 4px 12px rgba(0,0,0,0.15); border-radius: 4px; }
    .lab-card { transition: all 0.3s ease; }
    .lab-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .field-locked, .lab-imported { background-color: #f8f9fa !important; cursor: not-allowed; }
`;
document.head.appendChild(modalStyles);

// Inicializar el gestor de modales según el estado del documento
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { 
        window.modalManager = new ModalManager(); 
    });
} else {
    window.modalManager = new ModalManager();
}

// Exponer la clase para uso global
window.ModalManager = ModalManager;
