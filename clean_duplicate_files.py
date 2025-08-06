"""
Script para eliminar archivos duplicados en el repositorio.
Este script busca y elimina archivos con sufijo (1) en su nombre
que son típicamente generados al clonar o copiar archivos.
"""

import os
import glob
import shutil

def find_duplicate_files(base_dir):
    """
    Encuentra archivos con (1) en su nombre que probablemente sean duplicados.
    
    Args:
        base_dir: Directorio desde el cual buscar
        
    Returns:
        Lista de rutas a archivos duplicados
    """
    # Buscar archivos que terminen con (1).extensión
    duplicate_pattern = os.path.join(base_dir, "**", "* (1).*")
    duplicates = glob.glob(duplicate_pattern, recursive=True)
    
    # También buscar archivos que terminen con (1) sin extensión
    duplicate_pattern_no_ext = os.path.join(base_dir, "**", "* (1)")
    duplicates.extend(glob.glob(duplicate_pattern_no_ext, recursive=True))
    
    # Archivos específicos que sabemos son duplicados
    known_duplicates = [
        os.path.join(base_dir, 'app/parsers/lab_parser (1).py'),
        os.path.join(base_dir, 'app/parsers/pdf_extractor (1).py'),
        os.path.join(base_dir, 'app/main/routes (1).py'),
        os.path.join(base_dir, 'app/models/lab_result (1).py'),
        os.path.join(base_dir, 'app/models/report (1).py'),
        os.path.join(base_dir, 'app/models/__init__ (1).py'),
        os.path.join(base_dir, 'app/models/patient (1).py'),
        os.path.join(base_dir, 'app/api/gemini_client (1).py'),
        os.path.join(base_dir, 'app/api/routes (1).py'),
        os.path.join(base_dir, 'app/api/__init__ (1).py'),
        os.path.join(base_dir, 'app/__init__ (1).py')
    ]
    
    # Añadir los conocidos y eliminar duplicados
    all_duplicates = list(set(duplicates + known_duplicates))
    
    return all_duplicates

def main():
    """Ejecuta la limpieza de archivos duplicados."""
    print("Iniciando limpieza de archivos duplicados...")
    
    # Usar el directorio actual como base
    base_dir = os.getcwd()
    
    # Encontrar duplicados
    duplicates = find_duplicate_files(base_dir)
    
    # Eliminar los archivos duplicados
    count = 0
    for file_path in duplicates:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Eliminado: {os.path.relpath(file_path, base_dir)}")
                count += 1
            except Exception as e:
                print(f"❌ Error al eliminar {os.path.relpath(file_path, base_dir)}: {str(e)}")
        else:
            print(f"⚠️ No encontrado: {os.path.relpath(file_path, base_dir)}")
    
    print(f"\nProceso completado. {count} archivos eliminados.")

if __name__ == "__main__":
    main()
