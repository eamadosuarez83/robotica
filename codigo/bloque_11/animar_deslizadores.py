"""Anima curso_3gdl (3R antropomorfico) con un deslizador por
articulacion, dibujando los eslabones entre marcos consecutivos
(Bloque 11, Tema 11.5).

Correr con:
    python codigo/bloque_11/animar_deslizadores.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dh import marcos  # noqa: E402

L1, L2, L3 = 15.0, 12.0, 10.0  # cm
DH = [[0, L1, 0, np.pi / 2, 0], [0, 0, L2, 0, 0], [0, 0, L3, 0, 0]]


def main() -> None:
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(projection="3d")
    plt.subplots_adjust(bottom=0.28)

    def puntos(q_deg):
        q = np.radians(q_deg)
        Ms = marcos(DH, q)
        return np.array([M[:3, 3] for M in Ms])

    q0 = [0.0, 0.0, 0.0]
    pts = puntos(q0)
    linea, = ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], "o-", lw=4, ms=8, color="tab:blue")

    alcance = L1 + L2 + L3
    ax.set_xlim(-alcance, alcance)
    ax.set_ylim(-alcance, alcance)
    ax.set_zlim(0, alcance)
    ax.set_xlabel("x [cm]")
    ax.set_ylabel("y [cm]")
    ax.set_zlabel("z [cm]")
    ax.set_title("curso_3gdl — Bloque 11")

    ejes = [plt.axes([0.2, 0.16 - 0.05 * i, 0.6, 0.03]) for i in range(3)]
    sliders = [Slider(ejes[i], f"q{i+1} [°]", -180, 180, valinit=q0[i]) for i in range(3)]

    def actualizar(_):
        pts = puntos([s.val for s in sliders])
        linea.set_data(pts[:, 0], pts[:, 1])
        linea.set_3d_properties(pts[:, 2])
        fig.canvas.draw_idle()

    for s in sliders:
        s.on_changed(actualizar)

    plt.show()


if __name__ == "__main__":
    main()
