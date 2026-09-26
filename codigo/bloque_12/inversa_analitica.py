"""Inversa geometrica del 2R (Bloque 01) y del 3R antropomorfico real
curso_3gdl (Bloque 11), verificando cerrando el ciclo
inversa -> directa -> debe dar el punto pedido (Bloque 12, Temas
12.1-12.2).

Correr con:
    python codigo/bloque_12/inversa_analitica.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dh import directa  # noqa: E402
from robotica.inversa import inv_2r_geometrica, inv_3r_geometrica  # noqa: E402


def verificar_2r():
    L1, L2 = 0.30, 0.20
    dh = [[0, 0, L1, 0, 0], [0, 0, L2, 0, 0]]
    objetivo = np.array([0.298, 0.381])

    sol = inv_2r_geometrica(*objetivo, L1, L2)
    print("=== 2R plano (objetivo del Bloque 01) ===")
    for nombre, s in zip(("codo arriba", "codo abajo"), sol):
        p = directa(dh, s)[:2, 3]
        print(f"  {nombre}: q={np.round(np.degrees(s), 2)}° -> p={np.round(p, 4)}")
        assert np.allclose(p, objetivo, atol=1e-6)
    print("OK: ambas soluciones cierran el ciclo (inversa -> directa -> objetivo).\n")


def verificar_3r():
    L1, L2, L3 = 15.0, 12.0, 10.0   # cm, curso_3gdl real (robotica-manipuladores)
    dh = [[0, L1, 0, np.pi / 2, 0], [0, 0, L2, 0, 0], [0, 0, L3, 0, 0]]

    q_original = np.radians([30, 45, -20])
    objetivo = directa(dh, q_original)[:3, 3]

    sol = inv_3r_geometrica(*objetivo, L1, L2, L3)
    print("=== curso_3gdl (3R antropomórfico real) ===")
    print(f"Objetivo (generado con q={np.degrees(q_original)}°): {np.round(objetivo, 3)} cm")
    for nombre, s in zip(("codo arriba", "codo abajo"), sol):
        p = directa(dh, s)[:3, 3]
        print(f"  {nombre}: q={np.round(np.degrees(s), 2)}° -> p={np.round(p, 3)}")
        assert np.allclose(p, objetivo, atol=1e-6)
    print("OK: ambas soluciones cierran el ciclo.\n")

    print("Punto fuera de alcance:", inv_3r_geometrica(100, 0, 0, L1, L2, L3))


if __name__ == "__main__":
    verificar_2r()
    verificar_3r()
