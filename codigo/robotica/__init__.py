"""Libreria propia del curso de robotica.

Crece bloque a bloque. Por ahora:

- `vectores`: producto punto, producto cruz, normas, torque (Bloque 02).
- `graficar`: cuadriculas, vectores y marcos 2D (Bloque 03).
- `simular`: integradores Euler y RK4 (Bloque 05).
- `rotaciones`: rotx, roty, rotz, 3x3 (Bloque 08).
- `orientacion`: Euler RPY/ZXZ, eje-ángulo, cuaterniones, SLERP (Bloque 09).
- `homogeneas`: matrices de transformación homogénea 4x4 (Bloque 10).
- `dh`, `brazo`: Denavit-Hartenberg y cinemática directa (Bloque 11).
"""

from . import brazo, dh, graficar, homogeneas, orientacion, rotaciones, simular, vectores

__all__ = ["vectores", "graficar", "simular", "rotaciones", "orientacion",
           "homogeneas", "dh", "brazo"]
