"""Verifica que el entorno del curso esta listo.

Bloque 00. Correr con:
    python codigo/bloque_00/verificar_entorno.py

No modifica nada: solo revisa la version de Python y que los paquetes
necesarios se puedan importar, y avisa cuales son obligatorios desde
ya (Parte I) y cuales se instalan mas adelante.
"""

from __future__ import annotations

import importlib
import sys

VERSION_MINIMA = (3, 10)

# (nombre del paquete a importar, se necesita desde...)
OBLIGATORIOS = [
    ("numpy", "Bloque 00"),
    ("scipy", "Bloque 00"),
    ("sympy", "Bloque 00"),
    ("matplotlib", "Bloque 00"),
]

OPCIONALES = [
    ("spatialmath", "Bloque 08"),
    ("roboticstoolbox", "Bloque 11"),
    ("control", "Bloque 17"),
    ("pybullet", "Bloque 15"),
    ("serial", "Bloque 22"),
    ("schemdraw", "recursos/ (esquemas)"),
    ("graphviz", "recursos/ (esquemas)"),
]


def marca(ok: bool) -> str:
    return "✓" if ok else "✗"


def verificar_python() -> bool:
    actual = sys.version_info[:2]
    ok = actual >= VERSION_MINIMA
    print(f"[{marca(ok)}] Python {actual[0]}.{actual[1]} "
          f"(se requiere >= {VERSION_MINIMA[0]}.{VERSION_MINIMA[1]})")
    return ok


def verificar_paquete(nombre: str) -> tuple[bool, str]:
    try:
        modulo = importlib.import_module(nombre)
        version = getattr(modulo, "__version__", "sin version")
        return True, version
    except ImportError:
        return False, ""


def main() -> int:
    print("=== Verificación del entorno — Bloque 00 ===\n")

    todo_bien = verificar_python()

    print("\n--- Paquetes obligatorios (Parte I) ---")
    for nombre, desde in OBLIGATORIOS:
        ok, version = verificar_paquete(nombre)
        todo_bien = todo_bien and ok
        detalle = f"versión {version}" if ok else f"falta — necesario desde {desde}"
        print(f"[{marca(ok)}] {nombre:<15} {detalle}")

    print("\n--- Paquetes opcionales (se instalan cuando el bloque los pide) ---")
    for nombre, desde in OPCIONALES:
        ok, version = verificar_paquete(nombre)
        detalle = f"versión {version}" if ok else f"no instalado — se necesita desde {desde}"
        print(f"[{marca(ok)}] {nombre:<15} {detalle}")

    print()
    if todo_bien:
        print("Entorno listo para la Parte I del curso.")
    else:
        print("Faltan paquetes obligatorios. Correr:")
        print("    pip install -r requirements.txt")

    return 0 if todo_bien else 1


if __name__ == "__main__":
    raise SystemExit(main())
