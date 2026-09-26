"""Compara interpolar orientaciones con angulos de Euler (ingenuo,
linea recta en cada angulo) contra SLERP con cuaterniones, cerca de
un bloqueo del cardan (Bloque 09, Tema 9.6).

Correr con:
    python codigo/bloque_09/comparar_interpolacion.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.orientacion import (  # noqa: E402
    mat2cuaternion, mat2rpy, rpy2mat, slerp,
)

COLOR_X, COLOR_Y, COLOR_Z = "tab:red", "tab:green", "tab:blue"


def dibujar_marco(ax, R, origen, etiqueta=""):
    origen = np.asarray(origen, dtype=float)
    for i, color in enumerate([COLOR_X, COLOR_Y, COLOR_Z]):
        ax.quiver(*origen, *(R[:, i] * 0.8), color=color, linewidth=1.5)
    if etiqueta:
        ax.text(*(origen + [0, 0, 0.9]), etiqueta, fontsize=8)


def main() -> None:
    # Dos orientaciones cercanas a pitch=90° (bloqueo del cardán), separadas
    # en roll -- el caso donde Euler linealmente interpolado se comporta peor.
    R0 = rpy2mat(np.radians(-40), np.radians(80), np.radians(0))
    R1 = rpy2mat(np.radians(40), np.radians(80), np.radians(0))

    roll0, pitch0, yaw0 = mat2rpy(R0)
    roll1, pitch1, yaw1 = mat2rpy(R1)
    q0 = mat2cuaternion(R0)
    q1 = mat2cuaternion(R1)

    ts = np.linspace(0, 1, 6)

    fig, axes = plt.subplots(2, len(ts), figsize=(3 * len(ts), 6),
                              subplot_kw={"projection": "3d"})

    for j, t in enumerate(ts):
        # Interpolación ingenua: recta en cada ángulo de Euler
        roll_t = roll0 + t * (roll1 - roll0)
        pitch_t = pitch0 + t * (pitch1 - pitch0)
        yaw_t = yaw0 + t * (yaw1 - yaw0)
        R_euler = rpy2mat(roll_t, pitch_t, yaw_t)

        # SLERP sobre cuaterniones
        q_t = slerp(q0, q1, t)
        from robotica.orientacion import cuaternion2mat
        R_slerp = cuaternion2mat(q_t)

        dibujar_marco(axes[0, j], R_euler, origen=(0, 0, 0))
        axes[0, j].set_title(f"t={t:.1f}", fontsize=9)
        dibujar_marco(axes[1, j], R_slerp, origen=(0, 0, 0))

        for ax in (axes[0, j], axes[1, j]):
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.set_zlim(-1, 1)
            ax.set_axis_off()

    axes[0, 0].set_ylabel("Euler (ingenuo)")
    axes[1, 0].set_ylabel("SLERP")
    fig.suptitle("Interpolación cerca del bloqueo del cardán: "
                  "Euler ingenuo (arriba) vs. SLERP (abajo)")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
