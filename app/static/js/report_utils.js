document.addEventListener("DOMContentLoaded", function() {
    // El código existente del archivo

    // Función para llamar al backend
    const callBackend = async (endpoint, data) => {
        try {
            const response = await fetch(`/api/${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`Error en la petición: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                showAlert("Éxito", "Informe guardado correctamente", "success");
            } else {
                showAlert("Error", result.error || "Error desconocido", "error");
            }
            
            return result;
        } catch (error) {
            console.error("Error llamando al backend:", error);
            showAlert("Error", `No se pudo completar la operación: ${error.message}`, "error");
            return { success: false, error: error.message };
        }
    };
});
