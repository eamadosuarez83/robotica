"""Romperlo a proposito: una linea recta cartesiana del 2R que cruza
la singularidad de brazo estirado; la manipulabilidad cae a casi cero
a mitad de camino aunque resolver_trayectoria no reporte ningun error
(Bloque 19, Tema 19.5).

Correr con:
    python codigo/bloque_19/romper_singularidad_trayectoria.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.inversa import inv_2r_geometrica  # noqa: E402
from robotica.jacobiana import jacobiana_geometrica, manipulabilidad  # noqa: E402
from robotica.trayectorias import linea, resolver_trayectoria  # noqa: E402

L1, L2 = 0.30, 0.20
DH = [[0, 0, L1, 0, 0], [0, 0, L2, 0, 0]]


def main() -> None:
    # Línea que pasa justo por el brazo totalmente estirado (radio L1+L2).
    alcance = L1 + L2
    p1 = np.array([alcance * 0.7, alcance * 0.3, 0.0])
    p2 = np.array([alcance * 0.3, alcance * 0.7, 0.0])
    # Forzamos que pase exactamente por el punto de brazo estirado en el medio:
    medio = alcance * np.array([np.cos(np.radians(45)), np.sin(np.radians(45)), 0.0])
    puntos = np.vstack([linea(p1, medio, 15)[:-1], linea(medio, p2, 15)])

    inv = lambda px, py, pz: inv_2r_geometrica(px, py, L1, L2)  # noqa: E731
    resultado = resolver_trayectoria(puntos, inv)
    print("resolver_trayectoria:", resultado.estado, "-- ningún punto reportado como problema")

    manip = []
    for q in resultado.Q:
        J = jacobiana_geometrica(DH, q)[:2, :]
        manip.append(manipulabilidad(J))
    manip = np.array(manip)

    print(f"Manipulabilidad mínima a lo largo del camino: {manip.min():.6f} "
          f"(en el punto {np.argmin(manip)} de {len(manip)})")
    print(f"Manipulabilidad en los extremos: {manip[0]:.4f}, {manip[-1]:.4f}")
    print("Cae casi a cero a mitad de camino: ahí las velocidades articulares")
    print("necesarias para mantener velocidad cartesiana constante se disparan")
    print("(Bloque 13, Tema 13.5), aunque cada punto individual SÍ es alcanzable.")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
    ax1.plot(puntos[:, 0], puntos[:, 1], "o-", ms=3)
    ax1.plot(*medio[:2], "r*", ms=15, label="brazo estirado (singularidad)")
    ax1.set_aspect("equal")
    ax1.set_xlabel("x [m]")
    ax1.set_ylabel("y [m]")
    ax1.set_title("Línea cartesiana que cruza la singularidad")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(manip, color="tab:red")
    ax2.set_xlabel("punto a lo largo del camino")
    ax2.set_ylabel("manipulabilidad")
    ax2.set_title("Manipulabilidad a lo largo del camino")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
