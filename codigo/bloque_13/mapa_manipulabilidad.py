"""Mapa de manipulabilidad del 2R sobre su espacio de trabajo
(Bloque 13, Tema 13.6).

Correr con:
    python codigo/bloque_13/mapa_manipulabilidad.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dh import directa  # noqa: E402
from robotica.jacobiana import jacobiana_geometrica, manipulabilidad  # noqa: E402

L1, L2 = 0.30, 0.20
DH = [[0, 0, L1, 0, 0], [0, 0, L2, 0, 0]]


def main() -> None:
    t1s = np.linspace(-np.pi, np.pi, 120)
    t2s = np.linspace(-np.pi, np.pi, 120)

    xs, ys, ws = [], [], []
    for t1 in t1s:
        for t2 in t2s:
            p = directa(DH, [t1, t2])[:2, 3]
            J = jacobiana_geometrica(DH, [t1, t2])[:2, :]
            w = manipulabilidad(J)
            xs.append(p[0])
            ys.append(p[1])
            ws.append(w)

    # Verificación de la fórmula cerrada del Tema 13.6: w máximo en θ2=90°.
    t2_max_teorico = np.pi / 2
    w_max_teorico = L1 * L2 * np.sin(t2_max_teorico)
    print(f"Manipulabilidad máxima teórica (θ2=90°): {w_max_teorico:.4f}")
    print(f"Manipulabilidad máxima observada en la malla: {max(ws):.4f}")

    fig, ax = plt.subplots(figsize=(7, 6))
    sc = ax.scatter(xs, ys, c=ws, cmap="viridis", s=8)
    ax.set_aspect("equal")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Mapa de manipulabilidad del 2R\n(oscuro = cerca de singularidad)")
    plt.colorbar(sc, ax=ax, label="w = manipulabilidad")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
