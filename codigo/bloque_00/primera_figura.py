"""La primera figura del curso: un brazo de dos palitos que se mueve.

Bloque 00. Dos deslizadores controlan el angulo del hombro (theta1) y
del codo (theta2), en grados (solo para mostrarselos a una persona;
internamente se convierten a radianes antes de calcular, como manda
la convencion del curso). La formula que ubica la punta se explica
con detalle en el Bloque 01 (Tema 1.4); aqui solo se usa.

Correr con:
    python codigo/bloque_00/primera_figura.py
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

L1, L2 = 0.30, 0.20  # metros


def punta_2r(theta1_rad: float, theta2_rad: float) -> tuple[float, float]:
    x_codo = L1 * np.cos(theta1_rad)
    y_codo = L1 * np.sin(theta1_rad)
    x = x_codo + L2 * np.cos(theta1_rad + theta2_rad)
    y = y_codo + L2 * np.sin(theta1_rad + theta2_rad)
    return x_codo, y_codo, x, y


def main() -> None:
    fig, ax = plt.subplots(figsize=(6, 6))
    plt.subplots_adjust(bottom=0.28)

    theta1_0, theta2_0 = 40.0, 30.0
    x_codo, y_codo, x, y = punta_2r(np.radians(theta1_0), np.radians(theta2_0))

    linea, = ax.plot([0, x_codo, x], [0, y_codo, y], "o-", lw=4, ms=10, color="tab:blue")
    punto_base, = ax.plot([0], [0], "s", ms=12, color="k")

    alcance = L1 + L2
    ax.set_xlim(-alcance * 1.1, alcance * 1.1)
    ax.set_ylim(-alcance * 1.1, alcance * 1.1)
    ax.set_aspect("equal")
    ax.grid(True)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Brazo plano de dos eslabones — Bloque 00")

    eje_theta1 = plt.axes([0.2, 0.13, 0.6, 0.03])
    eje_theta2 = plt.axes([0.2, 0.07, 0.6, 0.03])
    slider_theta1 = Slider(eje_theta1, "hombro (°)", -180, 180, valinit=theta1_0)
    slider_theta2 = Slider(eje_theta2, "codo (°)", -180, 180, valinit=theta2_0)

    def actualizar(_):
        t1 = np.radians(slider_theta1.val)
        t2 = np.radians(slider_theta2.val)
        x_codo, y_codo, x, y = punta_2r(t1, t2)
        linea.set_data([0, x_codo, x], [0, y_codo, y])
        fig.canvas.draw_idle()

    slider_theta1.on_changed(actualizar)
    slider_theta2.on_changed(actualizar)

    plt.show()


if __name__ == "__main__":
    main()
