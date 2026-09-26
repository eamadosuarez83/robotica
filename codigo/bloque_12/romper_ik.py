"""Romperlo a proposito (Bloque 12, Temas 12.5 y 12.7):
1) pedir un punto fuera de alcance al metodo geometrico y al numerico,
   y comparar que devuelve cada uno, y
2) arrancar Newton-Raphson (pseudo-inversa, sin amortiguar) desde
   varias semillas, incluida una mala, y comparar la convergencia.

Correr con:
    python codigo/bloque_12/romper_ik.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dh import directa  # noqa: E402
from robotica.inversa import inv_2r_geometrica, inversa_numerica  # noqa: E402

L1, L2 = 0.30, 0.20
DH = [[0, 0, L1, 0, 0], [0, 0, L2, 0, 0]]


def parte1_fuera_de_alcance():
    objetivo = np.array([1.0, 0.0, 0.0])   # L1+L2 = 0.50 m: inalcanzable

    print("=== Punto fuera de alcance: (1.0, 0.0) con L1+L2=0.50 m ===")
    sol_geometrica = inv_2r_geometrica(objetivo[0], objetivo[1], L1, L2)
    print(f"Método geométrico devuelve: {sol_geometrica} (limpio, sin ambigüedad)")

    q, conv = inversa_numerica(DH, objetivo, [0.0, 0.0], metodo="amortiguado", max_iter=500)
    p_final = directa(DH, q)[:3, 3]
    error = np.linalg.norm(objetivo - p_final)
    print(f"Método numérico:  convergió={conv}, error final={error:.4f} m, p={np.round(p_final[:2],3)}")
    q_mas, _ = inversa_numerica(DH, objetivo, [0.0, 0.0], metodo="amortiguado", max_iter=20000)
    p_mas = directa(DH, q_mas)[:3, 3]
    print(f"  con 40x más iteraciones el residuo NO mejora más "
          f"(error={np.linalg.norm(objetivo - p_mas):.4f} m): el método se")
    print("  quedó en un punto estacionario, no le faltaban iteraciones. Esa es la señal")
    print("  de 'no hay solución', a diferencia de una convergencia lenta pero real.\n")


def parte2_semilla_mala():
    objetivo = np.array([0.298, 0.381, 0.0])

    print("=== Newton-Raphson (pseudo-inversa, sin amortiguar) desde varias semillas ===")
    semillas = {
        "buena (cerca de la solución)": [np.radians(35), np.radians(25)],
        "en el origen": [0.0, 0.0],
        "mala (codo casi estirado, cerca de singularidad)": [np.radians(1), np.radians(1)],
        "muy mala (extremo opuesto)": [np.radians(-170), np.radians(170)],
    }

    for nombre, q0 in semillas.items():
        q, conv = inversa_numerica(DH, objetivo, q0, metodo="pseudo_inversa", max_iter=1000)
        p = directa(DH, q)[:3, 3]
        error = np.linalg.norm(objetivo - p)
        print(f"  {nombre:52s} convergió={str(conv):5s}  error={error:.2e}")

    print("\nCon 'amortiguado' (mínimos cuadrados amortiguados), las mismas semillas:")
    for nombre, q0 in semillas.items():
        q, conv = inversa_numerica(DH, objetivo, q0, metodo="amortiguado", max_iter=1000)
        p = directa(DH, q)[:3, 3]
        error = np.linalg.norm(objetivo - p)
        print(f"  {nombre:52s} convergió={str(conv):5s}  error={error:.2e}")


if __name__ == "__main__":
    parte1_fuera_de_alcance()
    parte2_semilla_mala()
