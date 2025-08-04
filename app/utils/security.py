import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """Utilidad para validar y sanear datos de entrada."""
    
    @staticmethod
    def validate_patient_data(data):
        """
        Valida y sanea datos del paciente.
        
        Args:
            data (dict): Datos del paciente a validar
            
        Returns:
            dict: Datos saneados
            list: Errores encontrados
        """
        errors = []
        sanitized = {}
        
        # Requeridos
        required_fields = ['nombre', 'edad', 'sexo']
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Campo requerido: {field}")
        
        # Nombre
        if 'nombre' in data and data['nombre']:
            # Eliminar caracteres especiales excepto espacios y letras
            sanitized['nombre'] = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]', '', data['nombre'])
        
        # Edad
        if 'edad' in data and data['edad']:
            try:
                edad = int(data['edad'])
                if 0 <= edad <= 120:
                    sanitized['edad'] = edad
                else:
                    errors.append("Edad fuera de rango (0-120)")
            except ValueError:
                errors.append("Edad debe ser un número")
        
        # Sexo
        if 'sexo' in data and data['sexo']:
            sexo = data['sexo'].lower()
            if sexo in ['m', 'f']:
                sanitized['sexo'] = sexo
            else:
                errors.append("Sexo debe ser 'm' o 'f'")
        
        # Peso
        if 'peso' in data and data['peso']:
            try:
                peso = float(data['peso'])
                if 20 <= peso <= 300:
                    sanitized['peso'] = peso
                else:
                    errors.append("Peso fuera de rango (20-300 kg)")
            except ValueError:
                errors.append("Peso debe ser un número")
        
        # Talla
        if 'talla' in data and data['talla']:
            try:
                talla = float(data['talla'])
                if 50 <= talla <= 250:
                    sanitized['talla'] = talla
                else:
                    errors.append("Talla fuera de rango (50-250 cm)")
            except ValueError:
                errors.append("Talla debe ser un número")
        
        # Logs de seguridad
        if errors:
            logger.warning(f"Validación de datos de paciente falló: {errors}")
            
        return sanitized, errors

    @staticmethod
    def validate_lab_data(data):
        """
        Valida y sanea datos de laboratorio.
        
        Args:
            data (dict): Datos de laboratorio a validar
            
        Returns:
            dict: Datos saneados
            list: Errores encontrados
        """
        errors = []
        sanitized = {}
        
        valid_lab_keys = [
            'creatinina', 'glicemia', 'hba1c', 'ldl', 'hdl', 
            'trigliceridos', 'rac', 'albumina', 'pth', 'calcio',
            'fosforo', 'sodio', 'potasio', 'acido_urico'
        ]
        
        for key, value in data.items():
            if key not in valid_lab_keys:
                continue  # Ignorar claves no válidas
                
            try:
                val = float(value)
                # Límites generales para detectar valores absurdos
                if val < 0 or val > 10000:
                    errors.append(f"Valor fuera de rango para {key}: {val}")
                else:
                    sanitized[key] = val
            except (ValueError, TypeError):
                errors.append(f"Valor no numérico para {key}: {value}")
        
        return sanitized, errors