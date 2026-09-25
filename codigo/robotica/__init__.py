"""Libreria propia del curso de robotica.

Crece bloque a bloque. Por ahora:

- `vectores`: producto punto, producto cruz, normas, torque (Bloque 02).
- `graficar`: cuadriculas, vectores y marcos 2D (Bloque 03).
- `simular`: integradores Euler y RK4 (Bloque 05).
"""

from . import graficar, simular, vectores

__all__ = ["vectores", "graficar", "simular"]
