"""
Script para analizar y eliminar archivos duplicados
"""
import os
import filecmp
import sys

def find_duplicates(root_dir):
    """
    Encuentra archivos duplicados en el directorio especificado
    """
    duplicates = []
    
    # Buscar archivos con (1) en el nombre
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if " (1)" in filename:
                original_name = filename.replace(" (1)", "")
                original_path = os.path.join(dirpath, original_name)
                duplicate_path = os.path.join(dirpath, filename)
                
                if os.path.exists(original_path):
                    # Verificar si los archivos son idénticos
                    if filecmp.cmp(original_path, duplicate_path, shallow=False):
                        duplicates.append((original_path, duplicate_path, True))
                    else:
                        duplicates.append((original_path, duplicate_path, False))
    
    return duplicates

def print_results(duplicates):
    """
    Imprime los resultados del análisis de duplicados
    """
    print("\nAnálisis de archivos duplicados:")
    print("=" * 80)
    
    identical_count = 0
    different_count = 0
    
    for original, duplicate, is_identical in duplicates:
        status = "IDÉNTICO" if is_identical else "DIFERENTE"
        print(f"{status}: {os.path.basename(original)} <-> {os.path.basename(duplicate)}")
        
        if is_identical:
            identical_count += 1
        else:
            different_count += 1
    
    print("\nResumen:")
    print(f"Total de duplicados encontrados: {len(duplicates)}")
    print(f"  - Archivos idénticos: {identical_count}")
    print(f"  - Archivos diferentes: {different_count}")

def generate_removal_script(duplicates, output_file):
    """
    Genera un script para eliminar los duplicados idénticos
    """
    with open(output_file, 'w') as f:
        f.write("# Script para eliminar archivos duplicados\n\n")
        
        if os.name == 'nt':  # Windows
            f.write("# Ejecutar en PowerShell\n\n")
            for original, duplicate, is_identical in duplicates:
                if is_identical:
                    f.write(f'Remove-Item -Path "{duplicate}" -Force\n')
        else:  # Unix/Linux
            f.write("#!/bin/bash\n\n")
            for original, duplicate, is_identical in duplicates:
                if is_identical:
                    f.write(f'rm "{duplicate}"\n')
    
    print(f"\nScript de eliminación generado en: {output_file}")

if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.abspath(__file__))
    duplicates = find_duplicates(root_dir)
    
    if duplicates:
        print_results(duplicates)
        generate_removal_script(duplicates, "remove_duplicates.ps1")
    else:
        print("No se encontraron archivos duplicados.")
