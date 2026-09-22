"""Animador de transformaciones 2D: deslizadores a, b, c, d para la matriz
A = [[a, b], [c, d]]. Muestra como se deforma una cuadricula, el marco
x-y y el cuadrado unitario (su area es |det(A)|).

Bloque 03. Correr con:
    python codigo/bloque_03/animador_transformaciones.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica import graficar  # noqa: E402

CUADRADO = np.array([[0, 1, 1, 0, 0], [0, 0, 1, 1, 0]], dtype=float)


def main() -> None:
    fig, ax = plt.subplots(figsize=(6, 6))
    plt.subplots_adjust(bottom=0.32)
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    ax.set_aspect("equal")

    a0, b0, c0, d0 = 1.0, 0.0, 0.0, 1.0

    def redibujar(a, b, c, d):
        ax.clear()
        A = np.array([[a, b], [c, d]])
        graficar.dibujar_cuadricula(ax, A, rango=3.0)
        graficar.dibujar_marco2d(ax, A)
        cuadrado_t = A @ CUADRADO
        ax.plot(cuadrado_t[0], cuadrado_t[1], color="k", lw=1.5)
        det = a * d - b * c
        ax.set_xlim(-4, 4)
        ax.set_ylim(-4, 4)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
        ax.set_title(f"A = [[{a:.1f}, {b:.1f}], [{c:.1f}, {d:.1f}]]   "
                     f"det(A) = {det:.2f}")
        fig.canvas.draw_idle()

    redibujar(a0, b0, c0, d0)

    ejes = [plt.axes([0.2, 0.20 - 0.05 * i, 0.6, 0.03]) for i in range(4)]
    sliders = [
        Slider(ejes[0], "a", -3, 3, valinit=a0),
        Slider(ejes[1], "b", -3, 3, valinit=b0),
        Slider(ejes[2], "c", -3, 3, valinit=c0),
        Slider(ejes[3], "d", -3, 3, valinit=d0),
    ]

    def actualizar(_):
        redibujar(*(s.val for s in sliders))

    for s in sliders:
        s.on_changed(actualizar)

    plt.show()


if __name__ == "__main__":
    main()
