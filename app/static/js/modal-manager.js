/**
 * Gestor completo de modales para el proyecto ERC
 * Maneja apertura, cierre, eventos, notificaciones y edición manual de laboratorios importados
 * Versión mejorada con soporte ES6+ y mejor accesibilidad
 */
class ModalManager {
    constructor() {
        this.activeModals = new Set();
        this.modalStack = [];
        this.initialized = false;
        this.notifications = new Map();
        this.lastZIndex = 1050;
        this.focusStack = [];
        this.animations = new Map();
        
        // Exponer método de cierre globalmente
        window.closeModal = (modalId) => {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.style.display = 'none';
                document.body.classList.remove('modal-open');
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) backdrop.remove();
                console.log('[DEBUG] Modal cerrado (ModalManager):', modalId);
            }
        };
        
        this.init();
    }
    
    init() {
        if (this.initialized) return;
        
        try {
            this.setupGlobalListeners();
            this.setupExistingModals();
            this.setupAccessibility();
            this.setupAnimations();
            this.initialized = true;
            console.log('🎭 ModalManager mejorado inicializado correctamente');
        } catch (error) {
            console.error('❌ Error al inicializar ModalManager:', error);
        }
    }
    
    setupGlobalListeners() {
        // Evitar múltiples bindings
        if (this._globalListenersSet) return;
        this._globalListenersSet = true;

        // Captura para bloquear clicks al fondo cuando hay modales abiertos
        document.addEventListener('click', (e) => {
            if (this.modalStack.length === 0) return;
            const topModalId = this.modalStack[this.modalStack.length - 1];
            const topModalEl = document.getElementById(topModalId);
            if (!topModalEl) return;
            if (!e.target.closest('.modal') && !e.target.classList.contains('modal-backdrop')) {
                // Click fuera de cualquier modal mientras uno está abierto => bloquear
                e.stopPropagation();
                e.preventDefault();
                console.log('[DEBUG] Click bloqueado fuera de modal activo');
            }
        }, true);

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modalStack.length > 0) {
                e.preventDefault();
                const lastModal = this.modalStack[this.modalStack.length - 1];
                this.closeModal(lastModal);
                console.log('[DEBUG] Escape presionado, cerrando modal:', lastModal);
            }
        });
        
        document.addEventListener('click', (e) => {
            if (e.target) {
                console.log('[DEBUG] Click global:', e.target, 'clases:', e.target.className, 'id:', e.target.id);
            }
            // Backdrop
            if (e.target.classList.contains('modal-backdrop')) {
                e.preventDefault();
                e.stopPropagation();
                const lastModal = this.modalStack[this.modalStack.length - 1];
                if (lastModal) this.closeModal(lastModal);
                return;
            }
            // Botón de cierre (usar closest para íconos internos)
            const closeBtn = e.target.closest('[data-dismiss="modal"], [data-bs-dismiss="modal"], .close-modal, .modal-close, [aria-label="Close"], .btn-close');
            if (closeBtn) {
                const modal = closeBtn.closest('.modal');
                if (modal) {
                    e.preventDefault();
                    this.closeModal(modal.id || modal);
                }
                return;
            }
            // Click fuera del contenido del modal (sobre overlay interno del modal) => cerrar
            const modalEl = e.target.classList.contains('modal') ? e.target : e.target.closest('.modal');
            if (modalEl && !e.target.closest('.modal-dialog')) {
                this.closeModal(modalEl.id || modalEl);
            }
        });
    }
    
    setupExistingModals() {
        const closeSelectors = [
            '[data-dismiss="modal"]', '[data-bs-dismiss="modal"]', '.close', '.btn-close', 
            '.modal-close', '.modal-header .close', 'button[aria-label="Close"]'
        ];
        
        document.addEventListener('click', (e) => {
            if (closeSelectors.some(selector => e.target.matches && e.target.matches(selector))) {
                e.preventDefault();
                e.stopPropagation();
                const modalParent = e.target.closest('.modal') || e.target.closest('.modal-dialog') || e.target.closest('[role="dialog"]');
                if (modalParent) {
                    const modalElement = modalParent.classList.contains('modal') ? modalParent : modalParent.closest('.modal');
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
            if (!modal.id) {
                modal.id = modalId;
            }
        }
        
        if (!modal) {
            console.error(`Modal no encontrado:`, modalIdOrElement);
            return;
        }
        
        // Si ya está abierto, no hacer nada
        if (this.activeModals.has(modalId)) {
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
            backdrop.className = 'modal-backdrop fade';
            document.body.appendChild(backdrop);
            
            // Forzar un reflow para que la animación funcione
            backdrop.offsetHeight;
            backdrop.classList.add('show');
        }
        
        modal.dispatchEvent(new CustomEvent('modal:opened', { detail: { modalId } }));
        console.log(`Modal abierto: ${modalId}`, { 
            modalsActivos: [...this.activeModals],
            modalStack: [...this.modalStack]
        });
    }
    
    closeModal(modalIdOrElement) {
        let modal;
        let modalId;
        
        if (!modalIdOrElement) {
            console.warn('closeModal: No se proporcionó un modal para cerrar');
            return;
        }
        
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
                backdrop.classList.add('fade');
                setTimeout(() => {
                    if (backdrop && backdrop.parentNode) {
                        backdrop.parentNode.removeChild(backdrop);
                    }
                }, 150);
            }
            document.body.classList.remove('modal-open');
        }
        
        setTimeout(() => {
            modal.style.display = 'none';
            modal.classList.remove('fade');
            modal.removeAttribute('aria-modal');
            modal.removeAttribute('role');
            modal.dispatchEvent(new CustomEvent('modal:closed', { detail: { modalId } }));
            console.log(`Modal cerrado: ${modalId}`, { 
                modalsActivos: [...this.activeModals],
                modalStack: [...this.modalStack]
            });
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
        if (notification && notification.parentNode) {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => {
                if (notification && notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }
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
    
    // Nuevas funciones mejoradas
    setupAccessibility() {
        // Mejorar accesibilidad ARIA
        document.querySelectorAll('.modal').forEach(modal => {
            if (!modal.hasAttribute('role')) modal.setAttribute('role', 'dialog');
            if (!modal.hasAttribute('aria-modal')) modal.setAttribute('aria-modal', 'true');
            if (!modal.getAttribute('aria-labelledby')) {
                const title = modal.querySelector('.modal-title');
                if (title && title.id) modal.setAttribute('aria-labelledby', title.id);
            }
        });
    }
    
    setupAnimations() {
        // Configurar animaciones fluidas
        this.animations.set('fadeIn', { duration: 150, easing: 'ease-out' });
        this.animations.set('fadeOut', { duration: 150, easing: 'ease-in' });
    }
    
    manageFocus(modal, action) {
        if (action === 'trap') {
            // Guardar el elemento activo actual
            this.focusStack.push(document.activeElement);
            
            // Enfocar el primer elemento focuseable del modal
            const focusableElements = modal.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            if (focusableElements.length > 0) {
                focusableElements[0].focus();
            }
        } else if (action === 'restore') {
            // Restaurar el foco al elemento anterior
            const previousElement = this.focusStack.pop();
            if (previousElement && typeof previousElement.focus === 'function') {
                previousElement.focus();
            }
        }
    }
    
    async animateModal(modal, action) {
        if (!modal) return;
        
        const animationConfig = this.animations.get(action === 'show' ? 'fadeIn' : 'fadeOut');
        
        if (action === 'show') {
            modal.style.display = 'block';
            modal.style.opacity = '0';
            
            await new Promise(resolve => {
                requestAnimationFrame(() => {
                    modal.style.transition = `opacity ${animationConfig.duration}ms ${animationConfig.easing}`;
                    modal.style.opacity = '1';
                    setTimeout(resolve, animationConfig.duration);
                });
            });
        } else {
            modal.style.transition = `opacity ${animationConfig.duration}ms ${animationConfig.easing}`;
            modal.style.opacity = '0';
            
            await new Promise(resolve => setTimeout(resolve, animationConfig.duration));
            modal.style.display = 'none';
        }
    }
    
    // Método de ayuda para depuración mejorado
    debug() {
        console.group('🔍 ModalManager Debug Info');
        console.log('Active Modals:', [...this.activeModals]);
        console.log('Modal Stack:', [...this.modalStack]);
        console.log('Focus Stack Length:', this.focusStack.length);
        console.log('Body has modal-open class:', document.body.classList.contains('modal-open'));
        console.log('Backdrop exists:', !!document.querySelector('.modal-backdrop'));
        console.log('Visible modals count:', document.querySelectorAll('.modal.show').length);
        console.log('Notifications count:', this.notifications.size);
        console.groupEnd();
    }
}

// Añadir estilos CSS para animaciones y visualización
const modalStyles = document.createElement('style');
modalStyles.textContent = `
    @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
    @keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
    .notification-animate { animation: slideIn 0.3s ease-out; }
    .modal.fade { transition: opacity 0.15s linear; }
    .modal.show { display: block; opacity: 1; }
    .modal-backdrop.fade { transition: opacity 0.15s linear; }
    .modal-backdrop.show { opacity: 0.5; }
    .notification-toast { box-shadow: 0 4px 12px rgba(0,0,0,0.15); border-radius: 4px; }
    .lab-card { transition: all 0.3s ease; }
    .lab-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .field-locked, .lab-imported { background-color: #f8f9fa !important; cursor: not-allowed; }
    
    /* Safari y dispositivos móviles */
    @supports (-webkit-overflow-scrolling: touch) {
        .modal-open { position: fixed; width: 100%; }
    }
    
    /* Asegurar estilos robustos de modales y backdrop */
    .modal { position: fixed; top:0; left:0; width:100%; height:100%; overflow:auto; z-index:1050; display:none; background:rgba(0,0,0,0.05); }
    .modal.show { display:block; }
    .modal-dialog { position:relative; margin:1.5rem auto; pointer-events:auto; z-index:1060; }
    .modal-backdrop { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:1040; pointer-events:auto; }
    body.modal-open { overflow:hidden; }
    body.modal-open > *:not(.modal):not(.modal-backdrop) { /* impedir interacción fondo */ }
`;
document.head.appendChild(modalStyles);

// Inicializar el gestor de modales según el estado del documento
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { 
        // Comprobar si no existe ya una instancia
        if (!window.modalManager) {
            window.modalManager = new ModalManager(); 
            console.log('ModalManager inicializado al cargar el DOM');
        }
    });
} else {
    if (!window.modalManager) {
        window.modalManager = new ModalManager();
        console.log('ModalManager inicializado inmediatamente');
    }
}

// Exponer la clase para uso global
window.ModalManager = ModalManager;
