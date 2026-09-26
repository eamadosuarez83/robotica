"""Compara la trayectoria de la pinza del 2R interpolando en espacio
articular contra espacio cartesiano, para el mismo par de posturas
(Bloque 19, Tema 19.1).

Correr con:
    python codigo/bloque_19/comparar_espacios.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dh import directa  # noqa: E402
from robotica.inversa import inv_2r_geometrica  # noqa: E402
from robotica.trayectorias import interpolador_lineal, linea, resolver_trayectoria  # noqa: E402

L1, L2 = 0.30, 0.20
DH = [[0, 0, L1, 0, 0], [0, 0, L2, 0, 0]]


def main() -> None:
    theta1_0, theta2_0 = np.radians(20), np.radians(80)
    theta1_1, theta2_1 = np.radians(80), np.radians(20)

    # Espacio articular: interpolar cada ángulo por separado.
    Q1, _ = interpolador_lineal([np.degrees(theta1_0), np.degrees(theta1_1)], [0, 1], n_puntos=30)
    Q2, _ = interpolador_lineal([np.degrees(theta2_0), np.degrees(theta2_1)], [0, 1], n_puntos=30)
    pinza_articular = np.array([directa(DH, [np.radians(t1), np.radians(t2)])[:2, 3]
                                 for t1, t2 in zip(Q1, Q2)])

    # Espacio cartesiano: línea recta de la pinza, resuelta con la inversa.
    p_inicio = directa(DH, [theta1_0, theta2_0])[:2, 3]
    p_fin = directa(DH, [theta1_1, theta2_1])[:2, 3]
    puntos = linea([*p_inicio, 0], [*p_fin, 0], 30)
    inv = lambda px, py, pz: inv_2r_geometrica(px, py, L1, L2)  # noqa: E731
    resultado = resolver_trayectoria(puntos, inv, solucion=1)
    print("resolver_trayectoria:", resultado.estado)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot(pinza_articular[:, 0], pinza_articular[:, 1], "o-", ms=3,
            label="espacio articular (curva)")
    ax.plot(puntos[:, 0], puntos[:, 1], "s--", ms=3, color="tab:red",
            label="espacio cartesiano (línea recta)")
    ax.plot(*p_inicio, "k^", ms=10, label="inicio")
    ax.plot(*p_fin, "kv", ms=10, label="fin")
    ax.set_aspect("equal")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Mismo par de posturas: interpolar ángulos vs. interpolar la pinza")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
