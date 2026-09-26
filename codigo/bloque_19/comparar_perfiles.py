"""Compara posicion, velocidad y aceleracion de los perfiles lineal,
cubico, trapezoidal y S para el mismo movimiento (Bloque 19, Temas
19.2 y 19.3).

Correr con:
    python codigo/bloque_19/comparar_perfiles.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.trayectorias import (  # noqa: E402
    interpolador_cubico, interpolador_lineal, perfil_s, perfil_trapezoidal,
)


def main() -> None:
    q0, q1, T = 0.0, 90.0, 2.0
    n = 200

    Q_lin, t_lin = interpolador_lineal([q0, q1], [0, T], n_puntos=n)
    qd_lin = np.gradient(Q_lin, t_lin)
    qdd_lin = np.gradient(qd_lin, t_lin)

    t_cub, q_cub, qd_cub, qdd_cub = interpolador_cubico(q0, q1, 0, 0, T, n_puntos=n)

    Vp = (q1 - q0) / T * 1.5
    a = Vp / (T / 4)
    t_trap, q_trap, qd_trap, qdd_trap = perfil_trapezoidal(q0, q1, V=Vp, a=a, n_puntos=n)

    t_s, q_s, qd_s, qdd_s = perfil_s(q0, q1, T, n_puntos=n)

    fig, axes = plt.subplots(3, 1, figsize=(8, 9), sharex=True)
    datos = [
        ("Lineal", t_lin, Q_lin, qd_lin, qdd_lin),
        ("Cúbico", t_cub, q_cub, qd_cub, qdd_cub),
        ("Trapezoidal", t_trap, q_trap, qd_trap, qdd_trap),
        ("Perfil S", t_s, q_s, qd_s, qdd_s),
    ]
    for nombre, t, q, qd, qdd in datos:
        axes[0].plot(t, q, label=nombre)
        axes[1].plot(t, qd, label=nombre)
        axes[2].plot(t, qdd, label=nombre)

    axes[0].set_ylabel("posición [°]")
    axes[1].set_ylabel("velocidad [°/s]")
    axes[2].set_ylabel("aceleración [°/s²]")
    axes[2].set_xlabel("t [s]")
    axes[0].set_title("Lineal vs. cúbico vs. trapezoidal vs. perfil S (0° → 90°)")
    for ax in axes:
        ax.grid(True, alpha=0.3)
    axes[0].legend()
    plt.tight_layout()
    plt.show()

    print("Saltos de velocidad en t=0 (lineal tiene el salto más grande):")
    for nombre, t, q, qd, qdd in datos:
        print(f"  {nombre:15s} qd(0)={qd[0]:8.2f}  qdd(0)={qdd[0]:8.2f}")


if __name__ == "__main__":
    main()
