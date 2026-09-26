"""Romperlo a proposito: invertir una transformacion homogenea
transponiendo la matriz 4x4 completa (error clasico) en vez de usar
la formula T^-1 = [[R^T, -R^T p],[0,1]] (Bloque 10, Tema 10.5).

Correr con:
    python codigo/bloque_10/romper_inversa_transpuesta.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.homogeneas import inversa_homogenea, rt2homogenea  # noqa: E402
from robotica.rotaciones import rotz  # noqa: E402


def main() -> None:
    T = rt2homogenea(rotz(np.radians(90)), (1.0, 0.0, 0.0))

    T_inv_correcta = inversa_homogenea(T)
    T_inv_incorrecta = T.T   # error clásico: transponer TODA la matriz

    print("T =\n", np.round(T, 3))
    print("\nInversa correcta (R^T, -R^T p):\n", np.round(T_inv_correcta, 3))
    print("\nInversa incorrecta (T.T):\n", np.round(T_inv_incorrecta, 3))

    print(f"\nOrigen del marco con la inversa correcta:   {T_inv_correcta[:3, 3]}")
    print(f"Origen del marco con la inversa incorrecta: {T_inv_incorrecta[:3, 3]}")
    print("(el bloque de traslación de T.T no es -R^T p: es literalmente el vector p")
    print(" traspuesto sobre la última fila, que no tiene ningún significado geométrico)")

    print(f"\nT @ T_inv_correcta ≈ I:   {np.allclose(T @ T_inv_correcta, np.eye(4))}")
    print(f"T @ T_inv_incorrecta ≈ I: {np.allclose(T @ T_inv_incorrecta, np.eye(4))}")


if __name__ == "__main__":
    main()
