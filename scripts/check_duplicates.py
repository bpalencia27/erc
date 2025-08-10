"""Herramienta de verificación para detectar archivos duplicados que puedan causar conflictos.

Uso:
    python -m scripts.check_duplicates

Reglas:
 - Detecta sufijos ' (1).py', '.bak', '_backup', '__copy'.
 - Opcionalmente puede eliminar automáticamente (flag --fix) SOLO duplicados idénticos.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

DUPLICATE_PATTERNS = [" (1).py", ".bak", "_backup.py", "__copy.py"]

def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def find_duplicates(root: Path) -> List[Tuple[Path, Path]]:
    """Retorna pares (original, duplicado) basados en heurística de nombre y hash."""
    duplicates: List[Tuple[Path, Path]] = []
    for path in root.rglob('*.py'):
        if any(pat in path.name for pat in DUPLICATE_PATTERNS):
            base = path.name
            for pat in DUPLICATE_PATTERNS:
                base = base.replace(pat, '.py') if pat in base else base
            original = path.with_name(base)
            if original.exists():
                try:
                    if hash_file(original) == hash_file(path):
                        duplicates.append((original, path))
                except Exception:
                    pass
    return duplicates

def main():
    parser = argparse.ArgumentParser(description="Detecta archivos Python duplicados")
    parser.add_argument('--fix', action='store_true', help='Elimina duplicados idénticos')
    parser.add_argument('--root', default='.', help='Directorio raíz (default: .)')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    dups = find_duplicates(root)

    if not dups:
        print("✅ No se encontraron duplicados problemáticos")
        return

    print("⚠️ Duplicados detectados (original -> duplicado):")
    for orig, dup in dups:
        print(f" - {orig.relative_to(root)} -> {dup.relative_to(root)}")

    if args.fix:
        removed = 0
        for _, dup in dups:
            try:
                dup.unlink()
                removed += 1
            except Exception as e:
                print(f"No se pudo eliminar {dup}: {e}")
        print(f"🧹 Eliminados {removed} duplicados idénticos")
    else:
        print("Ejecuta con --fix para eliminar duplicados idénticos")

if __name__ == '__main__':
    main()
