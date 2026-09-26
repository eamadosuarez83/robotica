"""Romperlo a proposito: invertir el signo de calibracion de una
articulacion y ver como falla la cinematica inversa -- el brazo
persigue un punto calculado correctamente, pero el signo invertido
hace que el brazo FISICO termine en otro lado (Bloque 22, Tema 22.6).

Correr con:
    python codigo/bloque_22/romper_signo_invertido.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dh import directa  # noqa: E402
from robotica.inversa import inv_3r_geometrica  # noqa: E402

L1, L2, L3 = 0.15, 0.12, 0.10
DH = [[0, L1, 0, np.pi / 2, 0], [0, 0, L2, 0, 0], [0, 0, L3, 0, 0]]


def main() -> None:
    objetivo = np.array([0.15, 0.05, 0.20])
    sol = inv_3r_geometrica(*objetivo, L1, L2, L3)
    q_comandado = sol[0]
    print(f"Objetivo: {objetivo}")
    print(f"q comandado (°, calculado con cinemática inversa, Bloque 12): "
          f"{np.round(np.degrees(q_comandado), 2)}")

    print("\n=== Calibración correcta (signo = [1,1,1]) ===")
    p_real_ok = directa(DH, q_comandado)[:3, 3]
    print(f"Posición real del brazo físico: {np.round(p_real_ok, 4)}")
    print(f"Error: {np.linalg.norm(p_real_ok - objetivo)*100:.4f} cm")

    print("\n=== Calibración con signo invertido en la articulación 2 (codo) ===")
    for signo in ([1, -1, 1], [-1, 1, 1], [1, 1, -1]):
        q_fisico = np.array(signo) * q_comandado
        p_real = directa(DH, q_fisico)[:3, 3]
        error_cm = np.linalg.norm(p_real - objetivo) * 100
        print(f"  signo={signo}: posición real={np.round(p_real, 4)}, "
              f"error={error_cm:.2f} cm")

    print("\nUn signo de calibración equivocado en UNA sola articulación produce")
    print("un error de varios centímetros, aunque cada ángulo comandado sigue")
    print("dentro de sus límites articulares normales -- los límites por sí solos")
    print("(Bloque 07, Tema 22.6) no detectan este tipo de error.")


if __name__ == "__main__":
    main()
